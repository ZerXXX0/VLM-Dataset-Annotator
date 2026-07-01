import streamlit as st
from PIL import Image, ImageDraw
import config

def render_image(image_path, bboxes, selected_bbox_id, annotated_bbox_ids):
    """
    Render the original image with YOLO bounding boxes overlaid.
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

    draw = ImageDraw.Draw(img)
    
    for bbox in bboxes:
        bbox_id = bbox['bbox_id']
        x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
        
        # Determine color
        if bbox_id == selected_bbox_id:
            color = config.COLOR_SELECTED
            width = 3
        elif bbox_id in annotated_bbox_ids:
            color = config.COLOR_ANNOTATED
            width = 2
        else:
            color = config.COLOR_NOT_ANNOTATED
            width = 2
            
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
        
        # Draw confidence if available
        if bbox.get('confidence') is not None:
            conf_text = f"{bbox['confidence']:.2f}"
            # Simple text positioning
            draw.text((x1 + 2, y1 + 2), conf_text, fill=color)

    return img

def render_roi(image_path, bbox, expansion_pct=0):
    """
    Render an enlarged Region of Interest (ROI) based on the bounding box.
    expansion_pct is an integer from 0 to 50 representing percentage expansion.
    """
    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None
        
    width, height = img.size
    
    x1, y1, x2, y2 = bbox['x1'], bbox['y1'], bbox['x2'], bbox['y2']
    
    w_box = x2 - x1
    h_box = y2 - y1
    
    # Expand box
    expand_x = w_box * (expansion_pct / 100.0) / 2
    expand_y = h_box * (expansion_pct / 100.0) / 2
    
    new_x1 = max(0, int(x1 - expand_x))
    new_y1 = max(0, int(y1 - expand_y))
    new_x2 = min(width, int(x2 + expand_x))
    new_y2 = min(height, int(y2 + expand_y))
    
    roi = img.crop((new_x1, new_y1, new_x2, new_y2))
    
    return roi
