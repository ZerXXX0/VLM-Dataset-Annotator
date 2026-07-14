import os
from PIL import Image

def parse_yolo_label(file_path, image_width, image_height):
    """
    Parse a YOLO format label file and return bounding boxes in pixel coordinates.
    YOLO format: class x_center y_center width height (normalized 0-1)
    
    Returns a list of dicts:
    [{
        'bbox_id': int,
        'class_id': int,
        'x_center': float,
        'y_center': float,
        'width': float,
        'height': float,
        'x1': int,
        'y1': int,
        'x2': int,
        'y2': int,
        'confidence': float (optional)
    }]
    """
    bboxes = []
    if not os.path.exists(file_path):
        return bboxes

    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        parts = line.strip().split()
        if len(parts) >= 5:
            class_id = int(parts[0])
            x_center = float(parts[1])
            y_center = float(parts[2])
            width = float(parts[3])
            height = float(parts[4])
            
            # Confidence might be provided in some YOLO formats
            confidence = float(parts[5]) if len(parts) > 5 else None

            # Convert to pixel coordinates (x1, y1, x2, y2)
            w_px = width * image_width
            h_px = height * image_height
            
            # Skip extremely small/zero-size bounding boxes (dataset artifacts)
            if w_px < 2 or h_px < 2:
                continue
                
            x_center_px = x_center * image_width
            y_center_px = y_center * image_height
            
            x1 = int(x_center_px - w_px / 2)
            y1 = int(y_center_px - h_px / 2)
            x2 = int(x_center_px + w_px / 2)
            y2 = int(y_center_px + h_px / 2)
            
            # Bound within image
            x1 = max(0, min(x1, image_width))
            y1 = max(0, min(y1, image_height))
            x2 = max(0, min(x2, image_width))
            y2 = max(0, min(y2, image_height))

            bboxes.append({
                'bbox_id': idx,
                'class_id': class_id,
                'x_center': x_center,
                'y_center': y_center,
                'width': width,
                'height': height,
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'confidence': confidence
            })
            
    return bboxes
