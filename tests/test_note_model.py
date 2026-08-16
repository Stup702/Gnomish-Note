import unittest
from models.note_model import NoteModel, NOTE_TYPE_EMERGENCY, NOTE_TYPE_NORMAL

class TestNoteModel(unittest.TestCase):
    def test_default_values(self):
        m = NoteModel()
        self.assertIsNotNone(m.id)
        self.assertEqual(m.note_type, NOTE_TYPE_NORMAL)
        self.assertEqual(m.content_html, "")
        self.assertEqual(m.color, "#fdf5c9")
        self.assertEqual(m.font_color, "#333333")
        self.assertEqual(m.font_family, "Sans Serif")
        self.assertEqual(m.font_size, 11)
        self.assertEqual(m.width, 280)
        self.assertEqual(m.height, 320)
        self.assertFalse(m.minimized)

    def test_emergency_note_model(self):
        m = NoteModel(note_type=NOTE_TYPE_EMERGENCY)
        self.assertEqual(m.note_type, NOTE_TYPE_EMERGENCY)

    def test_serialization_roundtrip(self):
        m1 = NoteModel(
            id="test-123",
            note_type=NOTE_TYPE_EMERGENCY,
            content_html="<p>Important Task</p>",
            color="#ffcdd2",
            font_color="#111111",
            font_family="Monospace",
            font_size=14,
            pos_x=250,
            pos_y=350,
            width=320,
            height=400,
            minimized=False
        )
        d = m1.to_dict()
        m2 = NoteModel.from_dict(d)
        
        self.assertEqual(m1.id, m2.id)
        self.assertEqual(m1.note_type, m2.note_type)
        self.assertEqual(m1.content_html, m2.content_html)
        self.assertEqual(m1.color, m2.color)
        self.assertEqual(m1.font_color, m2.font_color)
        self.assertEqual(m1.font_family, m2.font_family)
        self.assertEqual(m1.font_size, m2.font_size)
        self.assertEqual(m1.pos_x, m2.pos_x)
        self.assertEqual(m1.pos_y, m2.pos_y)
        self.assertEqual(m1.width, m2.width)
        self.assertEqual(m1.height, m2.height)
        self.assertEqual(m1.minimized, m2.minimized)

    def test_from_dict_defaults_on_missing_fields(self):
        d = {"id": "partial-note"}
        m = NoteModel.from_dict(d)
        self.assertEqual(m.id, "partial-note")
        self.assertEqual(m.note_type, NOTE_TYPE_NORMAL)
        self.assertEqual(m.font_color, "#333333")
        self.assertEqual(m.font_size, 11)

if __name__ == "__main__":
    unittest.main()
