import streamlit as st
import datetime
import config

def render_annotation_panel(image_path, bbox, prompt_templates, current_annotation):
    """
    Render the annotation form for a selected bounding box.
    Returns a dictionary with the annotation data, or None if not submitted.
    """
    st.subheader("Annotation Form")
    
    # Ensure current_annotation is a dictionary
    if current_annotation is None:
        current_annotation = {}

    # Step 2: Select Prompt Template
    st.markdown("**Step 2: Select Prompt Template**")
    prompt_names = [t["name"] for t in prompt_templates]
    
    # Find index of current prompt if exists
    default_prompt_idx = 0
    if "prompt_name" in current_annotation:
        try:
            default_prompt_idx = prompt_names.index(current_annotation["prompt_name"])
        except ValueError:
            pass

    selected_prompt_name = st.selectbox(
        "Prompt Template", 
        prompt_names, 
        index=default_prompt_idx,
        key=f"prompt_sel_{image_path}_{bbox['bbox_id']}"
    )
    
    # Get the actual prompt text and replace coordinates
    selected_template = next((t for t in prompt_templates if t["name"] == selected_prompt_name), prompt_templates[0])
    prompt_text = selected_template["text"].format(
        x1=bbox['x1'], y1=bbox['y1'], x2=bbox['x2'], y2=bbox['y2']
    )
    st.text_area("Final Prompt", prompt_text, height=100, disabled=True, key=f"prompt_text_{image_path}_{bbox['bbox_id']}")

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

    # Step 4: Select Answer Template
    st.markdown("**Step 4: Select Answer Template**")
    answer_class_options = ["None"]
    if decision == "Weapon":
        answer_class_options += config.WEAPON_CLASSES
    elif decision == "Non-Weapon":
        answer_class_options += config.NON_WEAPON_CLASSES
        
    default_class_idx = 0
    if "answer_class" in current_annotation and current_annotation["answer_class"] in answer_class_options:
        default_class_idx = answer_class_options.index(current_annotation["answer_class"])
        
    # Callback to update reasoning text when answer template changes
    def on_template_change():
        selected_cls = st.session_state[f"ans_class_{image_path}_{bbox['bbox_id']}"]
        if selected_cls in config.DEFAULT_ANSWER_TEMPLATES:
            st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = config.DEFAULT_ANSWER_TEMPLATES[selected_cls]
        elif selected_cls == "None":
            st.session_state[f"reasoning_{image_path}_{bbox['bbox_id']}"] = ""

    answer_class = st.selectbox(
        "Answer Template", 
        answer_class_options, 
        index=default_class_idx,
        key=f"ans_class_{image_path}_{bbox['bbox_id']}",
        on_change=on_template_change
    )

    # Step 5: Reasoning Textbox
    st.markdown("**Step 5: Reasoning**")
    
    default_reasoning = current_annotation.get("reasoning", "")
    auto_reasoning = ""
    if answer_class != "None" and answer_class in config.DEFAULT_ANSWER_TEMPLATES:
        auto_reasoning = config.DEFAULT_ANSWER_TEMPLATES[answer_class]
        
    # Let user edit
    reasoning = st.text_area(
        "Reasoning (Editable)", 
        value=default_reasoning if default_reasoning else auto_reasoning,
        height=150,
        key=f"reasoning_{image_path}_{bbox['bbox_id']}"
    )

    # AI Assist Button
    if st.button("✨ Generate Draft (AI Assist)", key=f"ai_btn_{image_path}_{bbox['bbox_id']}"):
        st.info("AI Generation is a placeholder. Future integration with Qwen2-VL.")
        # We would update the reasoning field here if we had state management for it.

    # Step 6: Metadata
    st.markdown("**Step 6: Metadata (Optional)**")
    
    col1, col2 = st.columns(2)
    with col1:
        difficulty_idx = 0
        if "difficulty" in current_annotation and current_annotation["difficulty"] in config.DIFFICULTY_LEVELS:
            difficulty_idx = config.DIFFICULTY_LEVELS.index(current_annotation["difficulty"])
        difficulty = st.selectbox("Difficulty", config.DIFFICULTY_LEVELS, index=difficulty_idx, key=f"diff_{image_path}_{bbox['bbox_id']}")
        
    with col2:
        fp_idx = 0
        if "false_positive_category" in current_annotation and current_annotation["false_positive_category"] in config.FALSE_POSITIVE_CATEGORIES:
            fp_idx = config.FALSE_POSITIVE_CATEGORIES.index(current_annotation["false_positive_category"])
        fp_category = st.selectbox("False Positive Category", config.FALSE_POSITIVE_CATEGORIES, index=fp_idx, key=f"fp_{image_path}_{bbox['bbox_id']}")

    notes = st.text_input("Notes", value=current_annotation.get("notes", ""), key=f"notes_{image_path}_{bbox['bbox_id']}")
    
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
