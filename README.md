# VLM Studio Dataset Annotator

A Streamlit application for converting an existing YOLO object detection dataset into a Qwen2-VL instruction tuning dataset for semantic reasoning.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your YOLO dataset in a `dataset` folder with the following structure:
```
dataset/
    train/
        images/
        labels/
    valid/
        images/
        labels/
    test/
        images/
        labels/
```

3. Run the application:
```bash
streamlit run app.py
```

## User Manual: How to Annotate

The interface is divided into three main sections: the Navigation Sidebar (left), the Image Viewer (center), and the Annotation Panel (right).

### 1. Navigating Images
* Use the **Sidebar** to filter by dataset split (train, valid, test) or search for specific images.
* Empty images (no bounding boxes) are **automatically filtered out** to save time.
* Use the `Prev`, `Next`, and `Skip` buttons to cycle through the dataset. You can also use keyboard shortcuts (`A` for Prev, `D` for Next).
* **Jump to Image #:** Type an exact image number into the box to instantly teleport to it.
* **🚀 Jump to Next Unannotated:** Click this button to automatically scan your dataset and jump to the first image that is either untouched or partially finished.

### 2. The Image Viewer & Bounding Boxes
When an image is selected, the center panel displays the image with YOLO bounding boxes overlaid. You annotate one bounding box at a time.
* 🟦 **Blue (Thickest Line):** The current bounding box you are annotating.
* 🟩 **Green:** Bounding boxes you have already annotated and saved.
* 🟥 **Red:** Bounding boxes you have not yet annotated.
* Use the `Prev BBox` and `Next BBox` buttons (or `Arrow Left`/`Arrow Right` keys) to switch between objects in the same image.

### 3. The Annotation Workflow
For the active (Blue) bounding box, look at the **Annotation Panel** on the right side:
1. **Prompt Template:** Choose a base instruction prompt. The bounding box coordinates (e.g., `<box>(x1,y1,x2,y2)</box>`) will automatically be injected into the prompt.
2. **Final Decision:** This is **auto-detected** and locked based on the original YOLO dataset label (e.g., Class 2 = Weapon, Class 1 = Non-Weapon).
3. **Answer Template:** Select the specific subclass of the object (e.g., Handgun, Smartphone, Wallet). 
4. **Reasoning:** Once you select an Answer Template, a high-quality reasoning text will automatically generate in the text box. Review it, make any manual edits if necessary for the specific image, and click **Save Annotation**. 
5. The tool will automatically advance you to the next bounding box (or the next image if all boxes are complete).

### 4. Customizing Templates & Classes
If you need to add new object types (e.g., "Sniper Rifle"):
1. Open `config.py`.
2. Add the class name to the `WEAPON_CLASSES` or `NON_WEAPON_CLASSES` array.
3. Add a default reasoning text for it in the `DEFAULT_ANSWER_TEMPLATES` dictionary.

### 5. Exporting Data
When you are finished annotating, use the Export options in the sidebar:
* **Export to Qwen2-VL (JSONL):** Generates a conversational instruction-tuning dataset ready for Qwen2-VL training. The file is saved in the `exports/` folder.
* **Upload to Roboflow:** Enter your API credentials to push your dataset directly back to a Roboflow project workspace.

## Features Overview
- **Progress Auto-Saving:** The app generates an `internal_state.json` backup file. If you close your browser or restart your computer, it will flawlessly restore all your previous progress when you reopen the app!
- **Semantic Reasoning Annotation:** Add reasoning texts for bounding boxes from YOLO.
- **Export to Qwen2-VL:** Export annotations to the Qwen2-VL conversation format.
- **Template System:** Re-use prompts and reasoning templates to speed up the process.
- **Auto-Detection:** Inherits underlying dataset labels to enforce data consistency.
- **Modular Architecture:** Easy to extend and integrate with large language models in the future.

## Developer Documentation
For deep technical details on the system architecture, Streamlit UI state management, and the Product Requirements Document (PRD) for upgrading to a Next.js collaborative platform, please see the [Development Guide](DEVELOPMENT_GUIDE.md).
