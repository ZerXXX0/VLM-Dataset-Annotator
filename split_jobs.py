import os
import shutil
import json
import random
import glob

# Set random seed for reproducibility
random.seed(42)

# Define paths
SRC_DATASET = "dataset"
SRC_EXPORTS = "exports"
OUTPUT_DIR = "annotator_jobs"

# Targets (only images with annotations, total = 3602)
# Train: 1705, Valid: 1069, Test: 828
targets = {
    "person_1": {"train": 473, "valid": 297, "test": 230},
    "person_2": {"train": 473, "valid": 297, "test": 230},
    "me": {"train": 759, "valid": 475, "test": 368}  # remainders: 1705-946, 1069-594, 828-460
}

def get_image_label_pairs(split):
    img_dir = os.path.join(SRC_DATASET, split, "images")
    if not os.path.exists(img_dir):
        return []
    
    # Extensions
    exts = ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG')
    images = []
    for ext in exts:
        images.extend(glob.glob(os.path.join(img_dir, ext)))
    images = sorted(list(set(images)))
    
    pairs = []
    for img in images:
        base_name = os.path.splitext(os.path.basename(img))[0]
        lbl_dir = os.path.join(SRC_DATASET, split, "labels")
        lbl = os.path.join(lbl_dir, base_name + ".txt")
        if os.path.exists(lbl) and os.path.getsize(lbl) > 0:
            pairs.append((img, lbl))
    return pairs

def generate_exports_for_person(annotations, dataset_path, output_dir):
    def format_qwen2vl(image_rel_path, prompt, reasoning, decision):
        return {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "image", "image": image_rel_path},
                        {"type": "text", "text": prompt}
                    ]
                },
                {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": f"Reasoning:\n{reasoning}\n\nFinal Decision: {decision}"}
                    ]
                }
            ]
        }
        
    output_data_by_split = {}
    for image_path, bboxes in annotations.items():
        try:
            rel_image_path = os.path.relpath(image_path, start="dataset")
            split_name = rel_image_path.split(os.sep)[0]
        except Exception:
            rel_image_path = image_path
            split_name = "dataset"
            
        if split_name not in output_data_by_split:
            output_data_by_split[split_name] = []
            
        for bbox_id, ann in bboxes.items():
            if not all(k in ann for k in ['prompt', 'reasoning', 'decision']):
                continue
            formatted = format_qwen2vl(
                image_rel_path=rel_image_path,
                prompt=ann['prompt'],
                reasoning=ann['reasoning'],
                decision=ann['decision']
            )
            output_data_by_split[split_name].append(formatted)
            
    for split_name, data in output_data_by_split.items():
        if not data:
            continue
        # Export JSON
        out_json = os.path.join(output_dir, f'{split_name}.json')
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Export JSONL
        out_jsonl = os.path.join(output_dir, f'{split_name}.jsonl')
        with open(out_jsonl, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    # 1. Gather all pairs from each split
    split_pairs = {}
    for split in ["train", "valid", "test"]:
        pairs = get_image_label_pairs(split)
        # Shuffle to ensure representative distribution across jobs
        random.shuffle(pairs)
        split_pairs[split] = pairs
        print(f"Loaded {len(pairs)} pairs for split '{split}'")

    # 2. Distribute pairs to each target
    assignments = {
        "person_1": {"train": [], "valid": [], "test": []},
        "person_2": {"train": [], "valid": [], "test": []},
        "me": {"train": [], "valid": [], "test": []}
    }
    
    for split in ["train", "valid", "test"]:
        pairs = split_pairs[split]
        p1_count = targets["person_1"][split]
        p2_count = targets["person_2"][split]
        
        assignments["person_1"][split] = pairs[:p1_count]
        assignments["person_2"][split] = pairs[p1_count:p1_count + p2_count]
        assignments["me"][split] = pairs[p1_count + p2_count:]
        
        print(f"Distributed '{split}': person_1={len(assignments['person_1'][split])}, "
              f"person_2={len(assignments['person_2'][split])}, me={len(assignments['me'][split])}")

    # 3. Load internal state
    internal_state = {}
    state_file = os.path.join(SRC_EXPORTS, "internal_state.json")
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                internal_state = json.load(f)
            print(f"Loaded existing internal state with {len(internal_state)} entries.")
        except Exception as e:
            print(f"Error loading internal state: {e}")
    else:
        print("No existing internal_state.json found.")

    # 4. Write job folders
    if os.path.exists(OUTPUT_DIR):
        print(f"Removing existing output directory '{OUTPUT_DIR}' to start fresh...")
        shutil.rmtree(OUTPUT_DIR)
        
    for person in ["person_1", "person_2", "me"]:
        person_dir = os.path.join(OUTPUT_DIR, person)
        os.makedirs(person_dir, exist_ok=True)
        
        # Copy code files and folders to make it a self-contained streamlit app
        copy_items = ["app.py", "config.py", "requirements.txt", "templates.json", "README.md", ".gitignore"]
        for item in copy_items:
            if os.path.exists(item):
                shutil.copy(item, os.path.join(person_dir, item))
                
        # Copy components and utils directories
        for dir_name in ["components", "utils"]:
            if os.path.exists(dir_name):
                shutil.copytree(dir_name, os.path.join(person_dir, dir_name))
                
        # Create dataset folders
        person_dataset_dir = os.path.join(person_dir, SRC_DATASET)
        os.makedirs(person_dataset_dir, exist_ok=True)
        
        # Copy data.yaml and READMEs if they exist
        for f in ["data.yaml", "README.dataset.txt", "README.roboflow.txt"]:
            src_f = os.path.join(SRC_DATASET, f)
            if os.path.exists(src_f):
                shutil.copy(src_f, os.path.join(person_dataset_dir, f))
                
        # Copy assigned images and labels
        person_annotations = {}
        
        for split in ["train", "valid", "test"]:
            dest_img_dir = os.path.join(person_dataset_dir, split, "images")
            dest_lbl_dir = os.path.join(person_dataset_dir, split, "labels")
            os.makedirs(dest_img_dir, exist_ok=True)
            os.makedirs(dest_lbl_dir, exist_ok=True)
            
            for img_path, lbl_path in assignments[person][split]:
                # Copy image
                shutil.copy(img_path, os.path.join(dest_img_dir, os.path.basename(img_path)))
                # Copy label
                if lbl_path and os.path.exists(lbl_path):
                    shutil.copy(lbl_path, os.path.join(dest_lbl_dir, os.path.basename(lbl_path)))
                    
                # Check if this image has annotations in internal_state
                if img_path in internal_state:
                    person_annotations[img_path] = internal_state[img_path]

        # Write partitioned internal state
        person_exports_dir = os.path.join(person_dir, SRC_EXPORTS)
        os.makedirs(person_exports_dir, exist_ok=True)
        person_state_file = os.path.join(person_exports_dir, "internal_state.json")
        with open(person_state_file, 'w', encoding='utf-8') as f:
            json.dump(person_annotations, f, indent=2, ensure_ascii=False)
            
        generate_exports_for_person(person_annotations, person_dataset_dir, person_exports_dir)
        
        print(f"Created job folder for {person}: {len(person_annotations)} annotated entries imported.")

if __name__ == "__main__":
    main()
