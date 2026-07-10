import os
import json
import shutil

OUTPUT_DIR = "annotator_jobs"
FINAL_EXPORTS_DIR = "exports"
FINAL_DATASET_DIR = "dataset"

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

def main():
    merged_state = {}
    persons = ["person_1", "person_2", "me"]
    
    # 1. Merge internal state
    for person in persons:
        state_file = os.path.join(OUTPUT_DIR, person, "exports", "internal_state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    person_data = json.load(f)
                merged_state.update(person_data)
                print(f"Merged {len(person_data)} annotated entries from {person}")
            except Exception as e:
                print(f"Error reading {state_file}: {e}")
        else:
            print(f"Warning: No internal state found for {person} at {state_file}")
            
    # 2. Write merged internal state back to main workspace exports
    os.makedirs(FINAL_EXPORTS_DIR, exist_ok=True)
    merged_state_file = os.path.join(FINAL_EXPORTS_DIR, "internal_state.json")
    with open(merged_state_file, 'w', encoding='utf-8') as f:
        json.dump(merged_state, f, indent=2, ensure_ascii=False)
    print(f"Saved merged internal state to {merged_state_file} with {len(merged_state)} entries.")

    # 3. Export all merged annotations to train.json, train.jsonl, valid.json, etc.
    output_data_by_split = {}
    for image_path, bboxes in merged_state.items():
        try:
            rel_image_path = os.path.relpath(image_path, start=FINAL_DATASET_DIR)
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
            
    # Write the main exports files
    for split_name, data in output_data_by_split.items():
        if not data:
            continue
        # Export JSON
        out_json = os.path.join(FINAL_EXPORTS_DIR, f'{split_name}.json')
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Export JSONL
        out_jsonl = os.path.join(FINAL_EXPORTS_DIR, f'{split_name}.jsonl')
        with open(out_jsonl, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"Exported merged {split_name} split: {len(data)} bounding box annotations.")

if __name__ == "__main__":
    main()
