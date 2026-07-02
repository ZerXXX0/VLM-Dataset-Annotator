import os
import json

def format_qwen2vl(image_rel_path, prompt, reasoning, decision):
    """
    Format a single annotation into Qwen2-VL conversation format.
    """
    return {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_rel_path
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": f"Reasoning:\n{reasoning}\n\nFinal Decision: {decision}"
                    }
                ]
            }
        ]
    }

def save_internal_state(annotations, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    state_file = os.path.join(output_dir, 'internal_state.json')
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, indent=2, ensure_ascii=False)

def load_internal_state(output_dir):
    state_file = os.path.join(output_dir, 'internal_state.json')
    if not os.path.exists(state_file):
        return {}
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            converted = {}
            for img_path, bboxes in data.items():
                converted[img_path] = {}
                for bbox_id_str, ann in bboxes.items():
                    converted[img_path][int(bbox_id_str)] = ann
            return converted
    except Exception:
        return {}

def export_dataset(annotations, dataset_path, output_dir, format_type='jsonl'):
    """
    Export all annotations to files in Qwen2-VL format, separated by dataset split.
    annotations is a dict: { image_path: { bbox_id: annotation_dict } }
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    save_internal_state(annotations, output_dir)
        
    output_data_by_split = {}
    
    for image_path, bboxes in annotations.items():
        # Get relative path for the image, assuming dataset_path is the root
        try:
            rel_image_path = os.path.relpath(image_path, start=dataset_path)
            # The split folder name is typically the first part of the path (e.g., 'train', 'valid')
            split_name = rel_image_path.split(os.sep)[0]
        except ValueError:
            rel_image_path = image_path
            split_name = "dataset"
            
        if split_name not in output_data_by_split:
            output_data_by_split[split_name] = []
            
        for bbox_id, ann in bboxes.items():
            if not all(k in ann for k in ['prompt', 'reasoning', 'decision']):
                continue # Skip incomplete annotations
                
            formatted = format_qwen2vl(
                image_rel_path=rel_image_path,
                prompt=ann['prompt'],
                reasoning=ann['reasoning'],
                decision=ann['decision']
            )
            output_data_by_split[split_name].append(formatted)
            
    exported_files = []
    
    for split_name, data in output_data_by_split.items():
        if not data:
            continue
            
        if format_type == 'json':
            output_file = os.path.join(output_dir, f'{split_name}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            exported_files.append(output_file)
            
        elif format_type == 'jsonl':
            output_file = os.path.join(output_dir, f'{split_name}.jsonl')
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            exported_files.append(output_file)
            
    if exported_files:
        return ", ".join(os.path.basename(f) for f in exported_files)
        
    return None
