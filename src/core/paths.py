import os
import sys

def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource, works for dev and for PyInstaller bundle.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        # Development mode: base path is project root (parent of 'src')
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

def get_app_icon_path() -> str:
    """
    Returns path to the primary application icon.
    Prefers icons/gnomish-note.png, falls back to icons/gnomish-note-v4.png if present.
    """
    primary = get_resource_path(os.path.join("icons", "gnomish-note.png"))
    if os.path.exists(primary):
        return primary
    v4 = get_resource_path(os.path.join("icons", "gnomish-note-v4.png"))
    if os.path.exists(v4):
        return v4
    return primary
