import os

# Application Settings
APP_TITLE = "VLM Studio"
APP_ICON = "🖼️"

# Classes
WEAPON_CLASSES = [
    "Handgun", "Revolver", "Rifle", "Shotgun", "SMG", 
    "Assault Rifle", "Unknown Firearm"
]

NON_WEAPON_CLASSES = [
    "Smartphone", "Flashlight", "TV Remote", "Paper", "Book", "Wallet",
    "Toy Gun", "Camera", "Bottle", "Umbrella", "Power Tool", "Stick",
    "Hand Gesture", "Unknown Object", "Other"
]

# Metadata Options
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

FALSE_POSITIVE_CATEGORIES = [
    "None", "Phone", "Flashlight", "Paper", "Remote", "Tool", "Toy Gun",
    "Occlusion", "Blur", "Lighting", "Unknown", "Other"
]

# Paths
DATASET_PATH = "dataset"
OUTPUT_DIR = "exports"

# Colors for bounding boxes
COLOR_SELECTED = (0, 0, 255)      # Blue
COLOR_ANNOTATED = (0, 255, 0)     # Green
COLOR_NOT_ANNOTATED = (255, 0, 0) # Red
COLOR_HOVER = (255, 255, 0)       # Yellow

# Default Prompt Templates
DEFAULT_PROMPT_TEMPLATES = [
    {
        "id": "t1",
        "name": "Default Grounding",
        "text": "Analyze the object located inside the grounding bounding box <box>({x1},{y1},{x2},{y2})</box> and determine whether the object is a real firearm or a visually similar non-weapon object."
    },
    {
        "id": "t2",
        "name": "Reasoning First",
        "text": "Analyze the highlighted object located at <box>({x1},{y1},{x2},{y2})</box>.\nExplain your reasoning before deciding whether it is a firearm."
    },
    {
        "id": "t3",
        "name": "False Alarm Check",
        "text": "Inspect the highlighted object inside <box>({x1},{y1},{x2},{y2})</box>.\nDetermine if it is a real firearm or a false alarm."
    }
]

# Default Answer Templates (Reasoning text)
DEFAULT_ANSWER_TEMPLATES = {
    "Handgun": "The highlighted object exhibits characteristics consistent with a handgun, including a visible grip, trigger guard, and barrel. The object is being held in a manner consistent with firearm handling.",
    "Revolver": "The highlighted object exhibits a short barrel and overall geometry consistent with a revolver. The object is being held similarly to a firearm.",
    "Rifle": "The highlighted object is elongated and possesses features consistent with a rifle, including a stock, barrel, and handguard. The overall appearance and handling indicate a firearm.",
    "Shotgun": "The highlighted object is long and exhibits characteristics typical of a shotgun, including an elongated barrel and shoulder stock.",
    "Smartphone": "The object has a flat rectangular appearance without visible firearm components such as a trigger guard or barrel. The individual is holding it as if using a smartphone, which is consistent with smartphone usage rather than weapon handling.",
    "Flashlight": "The highlighted object appears cylindrical and lacks identifiable firearm components such as a trigger guard, grip, or barrel opening. Its appearance is consistent with a handheld flashlight.",
    "Paper": "The highlighted object appears thin, flat, and flexible without structural characteristics associated with firearms. Its visual appearance is consistent with paper.",
    "Book": "The object has a rectangular shape with proportions and appearance consistent with a book. No visible firearm components are present.",
    "Toy Gun": "Although the object resembles a firearm in overall shape, it lacks realistic firearm characteristics and appears consistent with a toy weapon.",
    "Unknown Object": "The object cannot be confidently identified due to image quality, occlusion, or insufficient visual information. No definitive firearm characteristics can be confirmed."
}
