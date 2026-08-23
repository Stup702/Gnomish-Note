import unittest
import sys
from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtGui import QTextDocumentFragment
from models.note_model import NoteModel, NOTE_TYPE_EMERGENCY, NOTE_TYPE_NORMAL
from note_manager import NoteManager
from windows.main_window import MainWindow, NoteListItem
import extension_installer

app = QApplication.instance() or QApplication(sys.argv)

class TestMainWindow(unittest.TestCase):
    def setUp(self):
        self.nm = NoteManager()
        self.mw = MainWindow(self.nm)

    def tearDown(self):
        self.nm.close_all_windows()
        self.mw.close()

    def test_preview_text_strips_css_tags(self):
        te = QTextEdit()
        te.setHtml("<p style='font-size: 20px;'>Clean User Text</p>")
        html = te.toHtml()
        
        # Verify that extracting via QTextDocumentFragment does not contain style/css
        clean = QTextDocumentFragment.fromHtml(html).toPlainText().strip()
        self.assertEqual(clean, "Clean User Text")
        self.assertNotIn("white-space", clean)
        self.assertNotIn("pre-wrap", clean)

    def test_list_sync_on_create_and_delete(self):
        note = self.nm.create_note(NOTE_TYPE_NORMAL)
        self.assertEqual(self.mw.list_widget.count(), 1)
        
        self.nm.delete_note(note.id)
        self.assertEqual(self.mw.list_widget.count(), 0)

    def test_custom_title_display(self):
        note = self.nm.create_note(NOTE_TYPE_NORMAL)
        note.title = "Grocery List"
        note.content_html = "<p>Milk, Eggs, Bread</p>"
        self.nm.update_note(note)
        
        item = self.mw.list_widget.item(0)
        widget = self.mw.list_widget.itemWidget(item)
        self.assertEqual("Grocery List", widget.title_label.text())
        self.assertIn("Milk, Eggs, Bread", widget.preview_label.text())

    def test_search_filtering(self):
        n1 = self.nm.create_note(NOTE_TYPE_NORMAL)
        n1.title = "Shopping"
        self.nm.update_note(n1)

        n2 = self.nm.create_note(NOTE_TYPE_NORMAL)
        n2.title = "Work Tasks"
        self.nm.update_note(n2)

        self.mw.search_input.setText("shop")
        self.assertFalse(self.mw.list_widget.item(0).isHidden())
        self.assertTrue(self.mw.list_widget.item(1).isHidden())

        self.mw.search_input.setText("")
        self.assertFalse(self.mw.list_widget.item(0).isHidden())
        self.assertFalse(self.mw.list_widget.item(1).isHidden())

    def test_click_item_reopens_closed_note(self):
        note = self.nm.create_note(NOTE_TYPE_NORMAL)
        win = self.nm._windows[note.id]
        
        # User closes the note
        win.hide()
        note.minimized = True
        self.nm.update_note(note)
        self.assertFalse(win.isVisible())
        
        # User clicks the note item in MainWindow
        item = self.mw.list_widget.item(0)
        widget = self.mw.list_widget.itemWidget(item)
        widget._open_note()
        
        self.assertTrue(win.isVisible())
        self.assertFalse(note.minimized)

    def test_extension_code_structure(self):
        ext_js = extension_installer.EXTENSION_JS_CODE
        # Verify that Alt-Tab filtering handles [Note] prefix and switcher classes
        self.assertIn("WindowSwitcherPopup", ext_js)
        self.assertIn("AppSwitcherPopup", ext_js)
        self.assertIn("[Note]", ext_js)
        self.assertIn("window.stick()", ext_js)
        self.assertIn("window.make_above()", ext_js)

if __name__ == "__main__":
    unittest.main()
