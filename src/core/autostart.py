import os
from pathlib import Path

AUTOSTART_FILENAME = "gnomish-note.desktop"

def get_autostart_dir() -> Path:
    config_home = os.environ.get("XDG_CONFIG_HOME")
    if config_home:
        return Path(config_home) / "autostart"
    return Path.home() / ".config" / "autostart"

def get_autostart_file_path() -> Path:
    return get_autostart_dir() / AUTOSTART_FILENAME

def is_autostart_enabled() -> bool:
    desktop_file = get_autostart_file_path()
    if not desktop_file.exists():
        return False
    try:
        content = desktop_file.read_text(encoding="utf-8")
        if "X-GNOME-Autostart-enabled=false" in content or "Hidden=true" in content:
            return False
        return True
    except Exception:
        return False

def enable_autostart() -> bool:
    try:
        autostart_dir = get_autostart_dir()
        autostart_dir.mkdir(parents=True, exist_ok=True)

        project_root = Path(__file__).resolve().parent.parent.parent
        main_py = project_root / "main.py"
        icon_path = project_root / "icons" / "gnomish-note-v4.png"

        content = f"""[Desktop Entry]
Name=Gnomish Note
GenericName=Sticky Notes
Comment=Sticky & Standard Notes for GNOME Linux
Exec=python3 {main_py} --autostart
Icon={icon_path}
Terminal=false
Type=Application
Categories=Utility;TextEditor;
StartupWMClass=gnomish-note
X-GNOME-Autostart-enabled=true
"""
        desktop_file = get_autostart_file_path()
        desktop_file.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"Failed to enable autostart: {e}")
        return False

def disable_autostart() -> bool:
    try:
        desktop_file = get_autostart_file_path()
        if desktop_file.exists():
            desktop_file.unlink()
        return True
    except Exception as e:
        print(f"Failed to disable autostart: {e}")
        return False

def toggle_autostart() -> bool:
    if is_autostart_enabled():
        disable_autostart()
    else:
        enable_autostart()
    return is_autostart_enabled()
