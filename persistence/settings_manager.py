from PyQt6.QtCore import QSettings

SETTINGS_ORG = "gnomish_note"
SETTINGS_APP = "defaults"

DEFAULTS = {
    "font_family": "Sans Serif",
    "font_size": 11,
    "color": "#fdf5c9",
    "font_color": "#333333",
    "width": 280,
    "height": 320
}

def get_default_settings() -> dict:
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    return {
        "font_family": settings.value("font_family", DEFAULTS["font_family"], type=str),
        "font_size": settings.value("font_size", DEFAULTS["font_size"], type=int),
        "color": settings.value("color", DEFAULTS["color"], type=str),
        "font_color": settings.value("font_color", DEFAULTS["font_color"], type=str),
        "width": settings.value("width", DEFAULTS["width"], type=int),
        "height": settings.value("height", DEFAULTS["height"], type=int),
    }

def save_default_settings(data: dict):
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    for key, value in data.items():
        settings.setValue(key, value)
    settings.sync()

def reset_default_settings():
    settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
    settings.clear()
    settings.sync()
