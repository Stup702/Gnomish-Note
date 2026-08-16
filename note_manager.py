from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from models.note_model import NoteModel, NOTE_TYPE_EMERGENCY, NOTE_TYPE_NORMAL
from persistence import storage
from windows.emergency_note import EmergencyNoteWindow
from windows.normal_note import NormalNoteWindow

class NoteManager(QObject):
    note_created = pyqtSignal(object)   # NoteModel instance
    note_deleted = pyqtSignal(str)      # note id
    note_updated = pyqtSignal(object)   # NoteModel instance

    def __init__(self):
        super().__init__()
        self._notes: dict[str, NoteModel] = {}
        self._windows = {}
        
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._do_save)

    def load_all(self):
        from PyQt6.QtWidgets import QApplication
        screen_geom = QApplication.primaryScreen().availableGeometry()
        
        loaded_notes = storage.load_notes()
        for note in loaded_notes:
            # Only reset if note is completely outside all monitor bounds
            if (note.pos_x < -note.width + 30 or
                note.pos_x > screen_geom.width() - 30 or
                note.pos_y < -note.height + 30 or
                note.pos_y > screen_geom.height() - 30):
                note.pos_x, note.pos_y = 100, 100
                
            self._notes[note.id] = note
            self._create_window_for_model(note)
            self.note_created.emit(note)

    def _create_window_for_model(self, model: NoteModel):
        if model.note_type == NOTE_TYPE_EMERGENCY:
            window = EmergencyNoteWindow(model=model, note_manager=self)
            self._windows[model.id] = window
            window.show()
            window.raise_()
        elif model.note_type == NOTE_TYPE_NORMAL:
            window = NormalNoteWindow(model=model, note_manager=self)
            self._windows[model.id] = window
            if not model.minimized:
                window.show()
                window.raise_()
            else:
                window.hide()

    def create_note(self, note_type: str) -> NoteModel:
        from persistence import settings_manager
        defaults = settings_manager.get_default_settings()
        
        model = NoteModel(
            note_type=note_type,
            font_family=defaults.get("font_family", "Sans Serif"),
            font_size=defaults.get("font_size", 11),
            color=defaults.get("color", "#fdf5c9"),
            font_color=defaults.get("font_color", "#333333"),
            width=defaults.get("width", 280),
            height=defaults.get("height", 320)
        )
        self._notes[model.id] = model
        self._create_window_for_model(model)
        self.note_created.emit(model)
        self.update_note(model)
        return model

    def delete_note(self, note_id: str):
        if note_id in self._windows:
            window = self._windows.pop(note_id)
            window.deleteLater()
        
        if note_id in self._notes:
            del self._notes[note_id]
            
        self.note_deleted.emit(note_id)
        self._do_save()

    def get_note(self, note_id: str) -> NoteModel | None:
        return self._notes.get(note_id)

    def update_note(self, model: NoteModel):
        self._notes[model.id] = model
        self.note_updated.emit(model)
        self._save_timer.start(500)

    def show_all(self):
        for model in self._notes.values():
            model.minimized = False
            self.update_note(model)
            window = self._windows.get(model.id)
            if window:
                window.show()
                window.raise_()

    def hide_all(self):
        for model in self._notes.values():
            model.minimized = True
            self.update_note(model)
            window = self._windows.get(model.id)
            if window:
                window.hide()

    def close_all_windows(self):
        for window in list(self._windows.values()):
            try:
                window.hide()
                window.close()
            except Exception:
                pass
        self._windows.clear()
        self._do_save()

    def _do_save(self):
        storage.save_notes(list(self._notes.values()))
