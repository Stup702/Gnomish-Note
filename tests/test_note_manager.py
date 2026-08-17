import unittest
import tempfile
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from models.note_model import NoteModel, NOTE_TYPE_EMERGENCY, NOTE_TYPE_NORMAL
from persistence import storage
from note_manager import NoteManager

app = QApplication.instance() or QApplication(sys.argv)

class TestNoteManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_data_dir = storage.DATA_DIR
        self.orig_data_file = storage.DATA_FILE
        
        storage.DATA_DIR = Path(self.temp_dir.name)
        storage.DATA_FILE = storage.DATA_DIR / "notes.json"
        
        self.nm = NoteManager()

    def tearDown(self):
        self.nm.close_all_windows()
        storage.DATA_DIR = self.orig_data_dir
        storage.DATA_FILE = self.orig_data_file
        self.temp_dir.cleanup()

    def test_create_and_get_note(self):
        note = self.nm.create_note(NOTE_TYPE_NORMAL)
        self.assertIsNotNone(note.id)
        self.assertEqual(note.note_type, NOTE_TYPE_NORMAL)
        
        fetched = self.nm.get_note(note.id)
        self.assertEqual(fetched.id, note.id)

    def test_delete_note(self):
        note = self.nm.create_note(NOTE_TYPE_EMERGENCY)
        self.assertIn(note.id, self.nm._notes)
        self.assertIn(note.id, self.nm._windows)
        
        self.nm.delete_note(note.id)
        self.assertNotIn(note.id, self.nm._notes)
        self.assertNotIn(note.id, self.nm._windows)

    def test_load_all_preserves_edge_positions(self):
        # Place note near edge (e.g. 0, 32)
        n = NoteModel(id="edge-note", pos_x=0, pos_y=32, width=280, height=320)
        storage.save_notes([n])
        
        nm2 = NoteManager()
        nm2.load_all()
        loaded = nm2.get_note("edge-note")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.pos_x, 0)
        self.assertEqual(loaded.pos_y, 32)
        nm2.close_all_windows()

    def test_show_all_and_hide_all(self):
        n1 = self.nm.create_note(NOTE_TYPE_NORMAL)
        self.nm.hide_all()
        self.assertTrue(self.nm.get_note(n1.id).minimized)
        
    def test_toggle_note_type(self):
        note = self.nm.create_note(NOTE_TYPE_NORMAL)
        self.assertEqual(note.note_type, NOTE_TYPE_NORMAL)
        from windows.normal_note import NormalNoteWindow
        self.assertIsInstance(self.nm._windows[note.id], NormalNoteWindow)

        # Toggle to Emergency (Sticky)
        updated = self.nm.toggle_note_type(note.id)
        self.assertEqual(updated.note_type, NOTE_TYPE_EMERGENCY)
        from windows.emergency_note import EmergencyNoteWindow
        self.assertIsInstance(self.nm._windows[note.id], EmergencyNoteWindow)

        # Toggle back to Normal
        updated2 = self.nm.toggle_note_type(note.id)
        self.assertEqual(updated2.note_type, NOTE_TYPE_NORMAL)
        self.assertIsInstance(self.nm._windows[note.id], NormalNoteWindow)

if __name__ == "__main__":
    unittest.main()
