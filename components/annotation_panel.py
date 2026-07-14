import streamlit as st
import datetime
import config
from components.templates import load_answer_templates

def render_annotation_panel(image_path, bbox, prompt_templates, current_annotation):
    """
    Render the annotation form for a selected bounding box.
    Returns a dictionary with the annotation data, or None if not submitted.
    """
    st.subheader("Annotation Form")
    
    # Ensure current_annotation is a dictionary
    if current_annotation is None:
        current_annotation = {}

    # Step 2: Prompt Template (UI deleted per user request, computed programmatically)
    if prompt_templates:
        saved_prompt_name = current_annotation.get("prompt_name")
        selected_template = next((t for t in prompt_templates if t["name"] == saved_prompt_name), prompt_templates[0])
    else:
        selected_template = {
            "name": "Default Grounding",
            "text": "Analyze the object located inside the grounding bounding box <box>({x1},{y1},{x2},{y2})</box> and determine whether the object is a real firearm or a visually similar non-weapon object."
        }
    selected_prompt_name = selected_template["name"]
    prompt_text = selected_template["text"].format(
        x1=bbox['x1'], y1=bbox['y1'], x2=bbox['x2'], y2=bbox['y2']
    )

    # Step 3: Select Final Decision (Auto-detected from YOLO label)
    st.markdown("**Step 3: Final Decision (Auto-detected from Dataset)**")
    
    # Map class_id to decision: 1 -> Non-Weapon, 2 -> Weapon
    class_id = bbox.get('class_id', -1)
    if class_id == 2:
        auto_decision = "Weapon"
    elif class_id == 1:
        auto_decision = "Non-Weapon"
    else:
        auto_decision = ""
        
    decision_options = ["", "Weapon", "Non-Weapon"]
    default_decision_idx = decision_options.index(auto_decision) if auto_decision in decision_options else 0
        
    decision = st.radio(
        "Final Decision", 
        decision_options, 
        index=default_decision_idx,
        key=f"decision_{image_path}_{bbox['bbox_id']}",
        horizontal=True,
        disabled=True
    )

    # Load custom answer templates and merge with defaults
    custom_templates = load_answer_templates()
    custom_weapons = [t["name"] for t in custom_templates if t["type"] == "Weapon"]
    custom_non_weapons = [t["name"] for t in custom_templates if t["type"] == "Non-Weapon"]

    # Combine default and custom answer templates for lookup
    all_answer_templates = dict(config.DEFAULT_ANSWER_TEMPLATES)
    for t in custom_templates:
        all_answer_templates[t["name"]] = t["text"]

    # Step 4: Select Answer Template
    st.markdown("**Step 4: Select Answer Template**")
    answer_class_options = ["None"]
    if decision == "Weapon":
        answer_class_options += config.WEAPON_CLASSES + custom_weapons
    elif decision == "Non-Weapon":
        answer_class_options += config.NON_WEAPON_CLASSES + custom_non_weapons
        
    default_class_idx = 0
    if "answer_class" in current_annotation:
        if current_annotation["answer_class"] in answer_class_options:
            default_class_idx = answer_class_options.index(current_annotation["answer_class"])
    else:
        if decision == "Weapon" and "Handgun" in answer_class_options:
            default_class_idx = answer_class_options.index("Handgun")
        elif decision == "Non-Weapon" and "Smartphone" in answer_class_options:
            default_class_idx = answer_class_options.index("Smartphone")
        
    # Callback to update reasoning text when answer template changes
    def on_template_change():
        selected_cls = st.session_state[f"ans_class_{image_path}_{bbox['bbox_id']}"]
        if selected_cls in all_answer_templates:
            st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = all_answer_templates[selected_cls]
        elif selected_cls == "None":
            st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = ""

    # Get current value and index
    sel_key = f"ans_class_{image_path}_{bbox['bbox_id']}"
    current_val = st.session_state.get(sel_key, answer_class_options[default_class_idx])
    if current_val in answer_class_options:
        current_idx = answer_class_options.index(current_val)
    else:
        current_idx = default_class_idx

    col_sel, col_prev, col_next = st.columns([6, 1, 1])
    
    with col_prev:
        if st.button("◀️", key=f"btn_prev_tpl_{image_path}_{bbox['bbox_id']}", use_container_width=True):
            new_idx = (current_idx - 1) % len(answer_class_options)
            st.session_state[sel_key] = answer_class_options[new_idx]
            selected_cls = answer_class_options[new_idx]
            if selected_cls in all_answer_templates:
                st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = all_answer_templates[selected_cls]
            elif selected_cls == "None":
                st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = ""
            st.rerun()

    with col_next:
        if st.button("▶️", key=f"btn_next_tpl_{image_path}_{bbox['bbox_id']}", use_container_width=True):
            new_idx = (current_idx + 1) % len(answer_class_options)
            st.session_state[sel_key] = answer_class_options[new_idx]
            selected_cls = answer_class_options[new_idx]
            if selected_cls in all_answer_templates:
                st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = all_answer_templates[selected_cls]
            elif selected_cls == "None":
                st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = ""
            st.rerun()

    with col_sel:
        answer_class = st.selectbox(
            "Answer Template", 
            answer_class_options, 
            index=current_idx,
            key=sel_key,
            on_change=on_template_change
        )

    # Step 5: Reasoning Textbox
    st.markdown("**Step 5: Reasoning**")
    
    default_reasoning = current_annotation.get("reasoning", "")
    auto_reasoning = ""
    if answer_class != "None" and answer_class in all_answer_templates:
        auto_reasoning = all_answer_templates[answer_class]
        
    # Let user edit
    reasoning = st.text_area(
        "Reasoning (Editable)", 
        value=default_reasoning if default_reasoning else auto_reasoning,
        height=150,
        key=f"reasoning_{image_path}_{bbox['bbox_id']}"
    )

    # Step 6: Metadata (UI deleted, set programmatically/defaulted)
    difficulty = current_annotation.get("difficulty", "Easy")
    fp_category = current_annotation.get("false_positive_category", "None")
    notes = current_annotation.get("notes", "")
    
    # Validation before return
    is_valid = True
    warnings = []
    
    if not decision:
        is_valid = False
        warnings.append("Final Decision is missing.")
    if not reasoning:
        is_valid = False
        warnings.append("Reasoning is missing.")
        
    for w in warnings:
        st.warning(w)

    annotation_data = {
        "prompt_name": selected_prompt_name,
        "prompt": prompt_text,
        "decision": decision,
        "answer_class": answer_class,
        "reasoning": reasoning,
        "difficulty": difficulty,
        "false_positive_category": fp_category,
        "notes": notes,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    return annotation_data, is_valid
