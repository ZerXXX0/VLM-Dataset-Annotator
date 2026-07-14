import streamlit as st
import os
import streamlit.components.v1 as components

# Set page config before any other Streamlit commands
st.set_page_config(
    page_title="VLM Studio",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import config
from components.navigation import render_navigation
from components.image_viewer import render_image, render_roi
from components.annotation_panel import render_annotation_panel
from components.templates import load_templates, render_template_manager
from utils.yolo import parse_yolo_label
from utils.dataset import get_label_path, get_image_info
from utils.exporter import export_dataset, load_internal_state

# Initialize session state for annotations
if 'annotations' not in st.session_state:
    st.session_state.annotations = load_internal_state(config.OUTPUT_DIR)

if 'selected_bbox_idx' not in st.session_state:
    st.session_state.selected_bbox_idx = 0

def main():
    # Handle pending image navigation before widgets are instantiated to prevent StreamlitAPIException
    if 'next_image_to_load' in st.session_state and st.session_state.next_image_to_load:
        st.session_state.image_selector_box = st.session_state.next_image_to_load
        del st.session_state.next_image_to_load

    # Inject keyboard shortcuts
    shortcuts_js = """
<script>
const doc = window.parent.document;
if (window.parent._shortcutListener) {
    doc.removeEventListener('keydown', window.parent._shortcutListener);
}
window.parent._shortcutListener = function(e) {
    const activeEl = doc.activeElement;
    if (activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA' || activeEl.isContentEditable)) {
        return;
    }

    let targetBtn = null;
    const buttons = Array.from(doc.querySelectorAll("button"));

    if (e.key === 'ArrowLeft') {
        targetBtn = buttons.find(b => b.innerText.includes("⏮️ Prev"));
    } else if (e.key === 'ArrowRight') {
        targetBtn = buttons.find(b => b.innerText.includes("⏭️ Next"));
    } else if (e.key === 'ArrowUp') {
        targetBtn = buttons.find(b => b.innerText.includes("Prev BBox"));
    } else if (e.key === 'ArrowDown') {
        targetBtn = buttons.find(b => b.innerText.includes("Next BBox"));
    } else if (e.key === '[') {
        targetBtn = buttons.find(b => b.innerText === "◀️");
    } else if (e.key === ']') {
        targetBtn = buttons.find(b => b.innerText === "▶️");
    } else if (e.key === 'Enter' || (e.ctrlKey && e.key === 'Enter')) {
        targetBtn = buttons.find(b => b.innerText.includes("Save Annotation"));
    }

    if (targetBtn) {
        e.preventDefault();
        targetBtn.click();
    }
};
doc.addEventListener('keydown', window.parent._shortcutListener);
</script>
"""
    components.html(shortcuts_js, height=0, width=0)

    # Render Sidebar Navigation
    split, selected_image_path = render_navigation()
    
    if not selected_image_path:
        st.info("Please select an image or ensure the dataset exists.")
        return

    # Load image info and labels
    img_width, img_height = get_image_info(selected_image_path)
    label_path = get_label_path(selected_image_path)
    bboxes = parse_yolo_label(label_path, img_width, img_height)

    # Initialize annotations for this image if not exists
    if selected_image_path not in st.session_state.annotations:
        st.session_state.annotations[selected_image_path] = {}

    annotated_bbox_ids = list(st.session_state.annotations[selected_image_path].keys())
    
    # Handle BBox Selection bounds
    if not bboxes:
        st.warning(f"No YOLO labels found for this image (expected at {label_path}).")
        st.session_state.selected_bbox_idx = 0
    else:
        st.session_state.selected_bbox_idx = max(0, min(st.session_state.selected_bbox_idx, len(bboxes) - 1))

    # --- MAIN LAYOUT ---
    # Three column layout: Left (handled by sidebar navigation partially, but main has left/center/right conceptually)
    # The prompt asked for: Left Panel, Center Panel, Right Panel
    # Streamlit sidebar = Left Panel
    # Center = Image Viewer
    # Right = ROI + Form
    
    col_center, col_right = st.columns([3, 2])

    with col_center:
        st.header("Image Viewer")
        
        # Bbox Navigation Buttons
        if bboxes:
            bb_col1, bb_col2, bb_col3 = st.columns([1, 1, 2])
            with bb_col1:
                if st.button("⬅️ Prev BBox", key="btn_prev_bbox"):
                    st.session_state.selected_bbox_idx = max(0, st.session_state.selected_bbox_idx - 1)
            with bb_col2:
                if st.button("Next BBox ➡️", key="btn_next_bbox"):
                    st.session_state.selected_bbox_idx = min(len(bboxes) - 1, st.session_state.selected_bbox_idx + 1)
            with bb_col3:
                st.markdown(f"**Current Bounding Box:** {st.session_state.selected_bbox_idx + 1} / {len(bboxes)}")
        
        # Render main image
        selected_bbox_id = bboxes[st.session_state.selected_bbox_idx]['bbox_id'] if bboxes else None
        
        if selected_image_path:
            rendered_img = render_image(
                image_path=selected_image_path,
                bboxes=bboxes,
                selected_bbox_id=selected_bbox_id,
                annotated_bbox_ids=annotated_bbox_ids
            )
            if rendered_img:
                st.image(rendered_img, use_container_width=True)
                
        # Template Manager Expander
        with st.expander("⚙️ Create New Template"):
            render_template_manager()

    with col_right:
        st.header("Annotation")
        
        if not bboxes:
            st.info("No bounding boxes to annotate.")
        else:
            selected_bbox = bboxes[st.session_state.selected_bbox_idx]
            

            # BBox Info
            st.markdown(f"**Coordinates:** ({selected_bbox['x1']}, {selected_bbox['y1']}) to ({selected_bbox['x2']}, {selected_bbox['y2']})")
            st.markdown(f"**Size:** {selected_bbox['width']*img_width:.1f} x {selected_bbox['height']*img_height:.1f} pixels")
            if selected_bbox.get('confidence') is not None:
                st.markdown(f"**YOLO Confidence:** {selected_bbox['confidence']:.2f}")
                
            st.markdown("---")
            
            # Annotation Form
            prompt_templates = load_templates()
            
            current_annotation = st.session_state.annotations[selected_image_path].get(selected_bbox['bbox_id'], {})
            
            annotation_data, is_valid = render_annotation_panel(selected_image_path, selected_bbox, prompt_templates, current_annotation)
            
            # Save button
            submitted = st.button("Save Annotation", type="primary", key=f"save_btn_{selected_image_path}_{selected_bbox['bbox_id']}")
            
            if submitted:
                if is_valid:
                    st.session_state.annotations[selected_image_path][selected_bbox['bbox_id']] = annotation_data
                    st.success("Annotation saved!")
                    
                    # Auto Save Dataset logic
                    if st.session_state.get('auto_save', True):
                        export_dataset(st.session_state.annotations, config.DATASET_PATH, config.OUTPUT_DIR, format_type='jsonl')
                        
                    # Move to next bbox or next image if all bboxes are annotated
                    if st.session_state.selected_bbox_idx < len(bboxes) - 1:
                        st.session_state.selected_bbox_idx += 1
                        st.rerun()
                    else:
                        from utils.dataset import get_images_in_split
                        images = get_images_in_split(config.DATASET_PATH, split)
                        if images and st.session_state.current_image_idx < len(images) - 1:
                            st.session_state.current_image_idx += 1
                            st.session_state.selected_bbox_idx = 0
                            st.session_state.next_image_to_load = images[st.session_state.current_image_idx]
                            st.rerun()
                        else:
                            st.success("All bounding boxes in this image annotated! This is the last image in the split.")
                else:
                    st.error("Please fill all required fields.")

if __name__ == "__main__":
    main()
