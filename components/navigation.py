import streamlit as st
import config
from utils.dataset import get_dataset_splits, get_images_in_split

def render_navigation():
    """
    Render the left navigation panel.
    Returns: split, selected_image_path
    """
    st.sidebar.title(f"{config.APP_ICON} {config.APP_TITLE}")
    
    dataset_path = config.DATASET_PATH
    splits = get_dataset_splits(dataset_path)
    
    if not splits:
        st.sidebar.warning(f"No dataset found at '{dataset_path}'. Please create the folder structure.")
        return None, None
        
    split = st.sidebar.selectbox("Split Selector", splits, key="split_selector")
    
    images = get_images_in_split(dataset_path, split)
    if not images:
        st.sidebar.warning(f"No images found in {split} split.")
        return split, None
        
    # State management for image index
    if 'current_image_idx' not in st.session_state:
        st.session_state.current_image_idx = 0
        
    # Reset index if split changes (handled roughly by checking if index is out of bounds)
    if st.session_state.current_image_idx >= len(images):
        st.session_state.current_image_idx = 0
        
    # Search
    search_query = st.sidebar.text_input("Image Search (Filename)")
    if search_query:
        filtered_images = [img for img in images if search_query.lower() in img.lower()]
        if filtered_images:
            images = filtered_images
            # We don't reset index here perfectly, but just bound it
            if st.session_state.current_image_idx >= len(images):
                st.session_state.current_image_idx = 0
    
    total_images = len(images)
    
    # Navigation Buttons
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if st.button("⏮️ Prev", key="btn_prev_img"):
            st.session_state.current_image_idx = max(0, st.session_state.current_image_idx - 1)
            st.session_state.selected_bbox_idx = 0
            if total_images > 0:
                st.session_state.image_selector_box = images[st.session_state.current_image_idx]
    with col2:
        if st.button("⏭️ Next", key="btn_next_img"):
            st.session_state.current_image_idx = min(total_images - 1, st.session_state.current_image_idx + 1)
            st.session_state.selected_bbox_idx = 0
            if total_images > 0:
                st.session_state.image_selector_box = images[st.session_state.current_image_idx]
    with col3:
        if st.button("⏭️ Skip", key="btn_skip_img"):
            st.session_state.current_image_idx = min(total_images - 1, st.session_state.current_image_idx + 1)
            st.session_state.selected_bbox_idx = 0
            if total_images > 0:
                st.session_state.image_selector_box = images[st.session_state.current_image_idx]

    # Auto Save Toggle
    st.session_state.auto_save = st.sidebar.checkbox("Auto Save", value=True)
    
    # Image Selector
    selected_image = st.sidebar.selectbox(
        "Image List", 
        images, 
        index=st.session_state.current_image_idx,
        key="image_selector_box"
    )
    
    # Update index if selected from dropdown
    if selected_image in images:
        new_idx = images.index(selected_image)
        if new_idx != st.session_state.current_image_idx:
            st.session_state.current_image_idx = new_idx
            st.session_state.selected_bbox_idx = 0

    # Progress
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Current Image:** {st.session_state.current_image_idx + 1} / {total_images}")
    progress = (st.session_state.current_image_idx + 1) / total_images if total_images > 0 else 0
    st.sidebar.progress(progress, text=f"Completion: {int(progress * 100)}%")

    # Shortcuts Info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Keyboard Shortcuts**")
    st.sidebar.markdown("""
    - `A`: Previous Image
    - `D`: Next Image
    - `Arrow Left`: Previous Bounding Box
    - `Arrow Right`: Next Bounding Box
    - `Ctrl+S`: Save
    - `Ctrl+Enter`: Save Annotation
    """)

    return split, selected_image
