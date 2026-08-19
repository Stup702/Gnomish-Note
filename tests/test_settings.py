import unittest
import sys
from PyQt6.QtWidgets import QApplication
from persistence import settings_manager
from note_manager import NoteManager
from windows.default_settings_dialog import DefaultSettingsDialog
from models.note_model import NOTE_TYPE_NORMAL

app = QApplication.instance() or QApplication(sys.argv)

class TestSettings(unittest.TestCase):
    def setUp(self):
        settings_manager.reset_default_settings()

    def tearDown(self):
        settings_manager.reset_default_settings()

    def test_default_settings_get_and_save(self):
        defaults = settings_manager.get_default_settings()
        self.assertEqual(defaults["font_family"], "Sans Serif")
        self.assertEqual(defaults["font_size"], 11)
        self.assertEqual(defaults["color"], "#fdf5c9")
        self.assertEqual(defaults["font_color"], "#333333")
        self.assertEqual(defaults["width"], 280)
        self.assertEqual(defaults["height"], 320)

        # Save custom defaults
        settings_manager.save_default_settings({
            "font_family": "Monospace",
            "font_size": 16,
            "color": "#e8f5e9",
            "font_color": "#004d40",
            "width": 350,
            "height": 450
        })

        updated = settings_manager.get_default_settings()
        self.assertEqual(updated["font_family"], "Monospace")
        self.assertEqual(updated["font_size"], 16)
        self.assertEqual(updated["color"], "#e8f5e9")
        self.assertEqual(updated["font_color"], "#004d40")
        self.assertEqual(updated["width"], 350)
        self.assertEqual(updated["height"], 450)

    def test_new_notes_inherit_configured_defaults(self):
        settings_manager.save_default_settings({
            "font_family": "Courier",
            "font_size": 18,
            "color": "#ffebee",
            "font_color": "#b71c1c",
            "width": 400,
            "height": 500
        })

        nm = NoteManager()
        note = nm.create_note(NOTE_TYPE_NORMAL)
        self.assertEqual(note.font_family, "Courier")
        self.assertEqual(note.font_size, 18)
        self.assertEqual(note.color, "#ffebee")
        self.assertEqual(note.font_color, "#b71c1c")
        self.assertEqual(note.width, 400)
        self.assertEqual(note.height, 500)
        nm.close_all_windows()

    def test_dialog_initialization(self):
        dlg = DefaultSettingsDialog()
        self.assertEqual(dlg.size_spin.value(), 11)
        self.assertEqual(dlg.width_spin.value(), 280)
        self.assertEqual(dlg.height_spin.value(), 320)
        dlg.close()

if __name__ == "__main__":
    unittest.main()
