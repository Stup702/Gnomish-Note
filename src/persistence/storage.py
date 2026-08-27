import json
import os
import logging
from pathlib import Path
from models.note_model import NoteModel

logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".local/share/gnome_linux_note_app"
DATA_FILE = DATA_DIR / "notes.json"

def load_notes() -> list[NoteModel]:
    if not DATA_FILE.exists():
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("JSON root is not a list")
            return [NoteModel.from_dict(d) for d in data]
    except Exception as e:
        logger.warning("Failed to load notes: %s. Renaming to notes.json.bak", e)
        try:
            bak_file = DATA_FILE.with_suffix(".json.bak")
            os.replace(DATA_FILE, bak_file)
        except OSError as rename_err:
            logger.error("Failed to rename corrupted notes file: %s", rename_err)
        return []

def save_notes(notes: list[NoteModel]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    tmp_file = DATA_FILE.with_suffix(".json.tmp")
    data = [note.to_dict() for note in notes]
    
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        
        os.replace(tmp_file, DATA_FILE)
    except Exception as e:
        logger.error("Failed to save notes: %s", e)
        if tmp_file.exists():
            try:
                tmp_file.unlink()
            except OSError:
                pass
