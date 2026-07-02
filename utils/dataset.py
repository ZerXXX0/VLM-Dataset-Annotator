import os
import glob
from PIL import Image

def get_dataset_splits(dataset_path):
    """
    Returns available dataset splits (e.g., train, valid, test) 
    found in the dataset directory.
    """
    splits = []
    if os.path.exists(dataset_path):
        for item in os.listdir(dataset_path):
            item_path = os.path.join(dataset_path, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'images')):
                splits.append(item)
    return sorted(splits)

def get_images_in_split(dataset_path, split):
    """
    Returns a sorted list of image file paths for a given split.
    """
    images_dir = os.path.join(dataset_path, split, 'images')
    if not os.path.exists(images_dir):
        return []
    
    # Common image extensions
    exts = ('*.jpg', '*.jpeg', '*.png')
    images = []
    for ext in exts:
        images.extend(glob.glob(os.path.join(images_dir, ext)))
        images.extend(glob.glob(os.path.join(images_dir, ext.upper())))
        
    # Filter images to only include those with non-empty label files
    filtered_images = []
    for img_path in sorted(list(set(images))):
        label_path = get_label_path(img_path)
        if os.path.exists(label_path) and os.path.getsize(label_path) > 0:
            # Optionally check if it contains actual text, but getsize > 0 is standard for YOLO
            filtered_images.append(img_path)
            
    return filtered_images

def get_label_path(image_path):
    """
    Returns the corresponding YOLO label path for a given image path.
    Assumes standard YOLO format: images/file.jpg -> labels/file.txt
    """
    dir_path = os.path.dirname(image_path)
    parent_dir = os.path.dirname(dir_path)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    label_dir = os.path.join(parent_dir, 'labels')
    label_path = os.path.join(label_dir, base_name + '.txt')
    return label_path

def get_image_info(image_path):
    """
    Returns image dimensions.
    """
    try:
        with Image.open(image_path) as img:
            return img.width, img.height
    except Exception:
        return 0, 0
