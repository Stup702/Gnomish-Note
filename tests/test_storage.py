import unittest
import tempfile
import os
from pathlib import Path
from models.note_model import NoteModel, NOTE_TYPE_EMERGENCY, NOTE_TYPE_NORMAL
from persistence import storage

class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.orig_data_dir = storage.DATA_DIR
        self.orig_data_file = storage.DATA_FILE
        
        storage.DATA_DIR = Path(self.temp_dir.name)
        storage.DATA_FILE = storage.DATA_DIR / "notes.json"

    def tearDown(self):
        storage.DATA_DIR = self.orig_data_dir
        storage.DATA_FILE = self.orig_data_file
        self.temp_dir.cleanup()

    def test_save_and_load_notes(self):
        n1 = NoteModel(id="n1", content_html="Hello 1")
        n2 = NoteModel(id="n2", note_type=NOTE_TYPE_EMERGENCY, content_html="Hello 2")
        
        storage.save_notes([n1, n2])
        self.assertTrue(os.path.exists(storage.DATA_FILE))
        
        loaded = storage.load_notes()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].id, "n1")
        self.assertEqual(loaded[0].content_html, "Hello 1")
        self.assertEqual(loaded[1].id, "n2")
        self.assertEqual(loaded[1].note_type, NOTE_TYPE_EMERGENCY)

    def test_load_corrupted_json(self):
        os.makedirs(storage.DATA_DIR, exist_ok=True)
        with open(storage.DATA_FILE, "w") as f:
            f.write("{ invalid json content ...")
            
        loaded = storage.load_notes()
        self.assertEqual(loaded, [])

    def test_load_non_existent_file(self):
        if os.path.exists(storage.DATA_FILE):
            os.remove(storage.DATA_FILE)
        loaded = storage.load_notes()
        self.assertEqual(loaded, [])

if __name__ == "__main__":
    unittest.main()
