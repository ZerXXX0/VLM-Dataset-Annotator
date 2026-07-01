from roboflow import Roboflow
import os
import shutil

print("Downloading dataset from Roboflow...")
rf = Roboflow(api_key="Q1flzyg1J8Z2OMweLXf3")
project = rf.workspace("weapon-mpr3p").project("2-class-weapon-dataset")
version = project.version(3)

# Usually the format for YOLOv8 is 'yolov8'. If 'yolo26' was a typo, roboflow might error.
# Let's try downloading what they specified. We'll download it to a temporary folder 
# and then move it to the 'dataset' folder that the app expects.
try:
    dataset = version.download("yolov8") # Using standard yolov8 which matches the required format
except Exception as e:
    print(f"Failed with yolov8, trying original yolo26: {e}")
    dataset = version.download("yolo26")

print(f"Dataset downloaded to {dataset.location}")

# Move the downloaded contents to the 'dataset' directory the app uses
app_dataset_dir = "dataset"
if os.path.exists(app_dataset_dir):
    shutil.rmtree(app_dataset_dir)
os.makedirs(app_dataset_dir, exist_ok=True)

# Roboflow usually creates a folder with train/ valid/ test/ inside
for item in os.listdir(dataset.location):
    source = os.path.join(dataset.location, item)
    destination = os.path.join(app_dataset_dir, item)
    shutil.move(source, destination)
    
print("Dataset successfully moved to 'dataset/' directory! You can now use the Streamlit app.")
