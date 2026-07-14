import json
import os
import streamlit as st
import config

TEMPLATES_FILE = "templates.json"
ANSWER_TEMPLATES_FILE = "answer_templates.json"

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

def load_answer_templates():
    """
    Load custom answer templates from JSON.
    """
    if not os.path.exists(ANSWER_TEMPLATES_FILE):
        return []
    try:
        with open(ANSWER_TEMPLATES_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading answer templates: {e}")
        return []

def save_answer_templates(templates):
    """
    Save custom answer templates to JSON.
    """
    try:
        with open(ANSWER_TEMPLATES_FILE, "w") as f:
            json.dump(templates, f, indent=4)
    except Exception as e:
        st.error(f"Error saving answer templates: {e}")

def render_template_manager():
    """
    Render UI for creating a new answer template.
    """
    st.subheader("Create New Answer Template")
    
    new_t_name = st.text_input("Template Name (Class)", key="new_t_name")
    new_t_text = st.text_area("Reasoning Text", key="new_t_text", height=100)
    new_t_type = st.selectbox("Category", ["Weapon", "Non-Weapon"], key="new_t_type")
    
    if st.button("Create Template"):
        if new_t_name and new_t_text:
            custom_templates = load_answer_templates()
            # Check if template with this name already exists
            if any(t["name"] == new_t_name for t in custom_templates):
                st.error("A template with this name already exists.")
            else:
                custom_templates.append({
                    "name": new_t_name,
                    "text": new_t_text,
                    "type": new_t_type
                })
                save_answer_templates(custom_templates)
                st.success(f"Created answer template for '{new_t_name}'!")
                st.rerun()
        else:
            st.warning("Please provide both template name and reasoning text.")
