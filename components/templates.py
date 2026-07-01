import json
import os
import streamlit as st
import config

TEMPLATES_FILE = "templates.json"

def load_templates():
    """
    Load prompt templates from JSON. If not found, create from defaults.
    """
    if not os.path.exists(TEMPLATES_FILE):
        save_templates(config.DEFAULT_PROMPT_TEMPLATES)
        return config.DEFAULT_PROMPT_TEMPLATES
        
    try:
        with open(TEMPLATES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading templates: {e}")
        return config.DEFAULT_PROMPT_TEMPLATES

def save_templates(templates):
    """
    Save prompt templates to JSON.
    """
    try:
        with open(TEMPLATES_FILE, "w") as f:
            json.dump(templates, f, indent=4)
    except Exception as e:
        st.error(f"Error saving templates: {e}")

def render_template_manager():
    """
    Render UI for managing prompt templates.
    """
    st.subheader("Manage Prompt Templates")
    templates = load_templates()
    
    # List existing templates
    for i, t in enumerate(templates):
        with st.expander(f"{t['name']}", expanded=False):
            new_name = st.text_input("Name", value=t['name'], key=f"t_name_{i}")
            new_text = st.text_area("Prompt Text", value=t['text'], height=100, key=f"t_text_{i}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Update", key=f"t_upd_{i}"):
                    templates[i]['name'] = new_name
                    templates[i]['text'] = new_text
                    save_templates(templates)
                    st.success("Updated!")
                    st.rerun()
            with col2:
                if len(templates) > 1:
                    if st.button("Delete", key=f"t_del_{i}"):
                        templates.pop(i)
                        save_templates(templates)
                        st.success("Deleted!")
                        st.rerun()

    st.markdown("---")
    st.markdown("**Create New Template**")
    new_t_name = st.text_input("New Template Name", key="new_t_name")
    new_t_text = st.text_area("New Prompt Text (use {x1},{y1},{x2},{y2} for bbox)", key="new_t_text")
    if st.button("Create Template"):
        if new_t_name and new_t_text:
            new_id = f"t_{len(templates) + 1}"
            templates.append({
                "id": new_id,
                "name": new_t_name,
                "text": new_t_text
            })
            save_templates(templates)
            st.success("Created!")
            st.rerun()
        else:
            st.warning("Please provide both name and text.")
