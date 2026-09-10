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
        loaded_notes.sort(key=lambda n: getattr(n, 'z_index', 0))
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
        
        max_z = max((n.z_index for n in self._notes.values()), default=0)
        model = NoteModel(
            note_type=note_type,
            font_family=defaults.get("font_family", "Sans Serif"),
            font_size=defaults.get("font_size", 11),
            color=defaults.get("color", "#fdf5c9"),
            font_color=defaults.get("font_color", "#333333"),
            width=defaults.get("width", 280),
            height=defaults.get("height", 320),
            opacity=defaults.get("opacity", 1.0),
            z_index=max_z + 1
        )
        self._notes[model.id] = model
        self._create_window_for_model(model)
        self.note_created.emit(model)
        self.update_note(model)
        return model

    def bring_to_front(self, note_id: str):
        model = self._notes.get(note_id)
        if not model:
            return

        other_z = [n.z_index for n in self._notes.values() if n.id != note_id]
        max_other = max(other_z, default=0) if other_z else 0
        if model.z_index <= max_other:
            model.z_index = max_other + 1
            self.update_note(model)

        window = self._windows.get(note_id)
        if window:
            if model.minimized:
                model.minimized = False
                self.update_note(model)
                window.show()
            if hasattr(window, 'isMinimized') and window.isMinimized():
                window.showNormal()
            window.raise_()
            window.activateWindow()

    def toggle_note_type(self, note_id: str) -> NoteModel | None:
        model = self._notes.get(note_id)
        if not model:
            return None

        # Capture current window position and geometry before closing
        old_window = self._windows.pop(note_id, None)
        if old_window:
            model.pos_x = old_window.pos().x()
            model.pos_y = old_window.pos().y()
            model.width = old_window.width()
            if not getattr(model, 'collapsed', False):
                model.height = old_window.height()
                model.expanded_height = old_window.height()
            old_window.close()
            old_window.deleteLater()

        # Switch type
        if model.note_type == NOTE_TYPE_EMERGENCY:
            model.note_type = NOTE_TYPE_NORMAL
        else:
            model.note_type = NOTE_TYPE_EMERGENCY

        # Re-create window with new type
        self._create_window_for_model(model)
        self.bring_to_front(note_id)
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
        sorted_notes = sorted(self._notes.values(), key=lambda n: getattr(n, 'z_index', 0))
        for model in sorted_notes:
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
