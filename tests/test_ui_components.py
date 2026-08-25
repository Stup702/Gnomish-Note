import unittest
import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QKeyEvent, QMouseEvent
from models.note_model import NoteModel, NOTE_TYPE_EMERGENCY, NOTE_TYPE_NORMAL
from note_manager import NoteManager
from windows.emergency_note import EmergencyNoteWindow
from windows.normal_note import NormalNoteWindow
from widgets.settings_popover import SettingsPopover
from widgets.resize_handle import ResizeHandle

app = QApplication.instance() or QApplication(sys.argv)

class TestUIComponents(unittest.TestCase):
    def setUp(self):
        self.nm = NoteManager()

    def tearDown(self):
        self.nm.close_all_windows()

    def test_emergency_note_window_properties(self):
        m = NoteModel(note_type=NOTE_TYPE_EMERGENCY)
        win = EmergencyNoteWindow(m, self.nm)
        flags = win.windowFlags()
        self.assertTrue(bool(flags & Qt.WindowType.FramelessWindowHint))
        self.assertTrue(bool(flags & Qt.WindowType.WindowStaysOnTopHint))
        self.assertTrue(bool(flags & Qt.WindowType.Window))
        # TopBar should NOT have close button for emergency note
        self.assertIsNone(win._content_widget.top_bar.btn_close)
        # Text edit should have StrongFocus
        self.assertEqual(win._content_widget.text_edit.focusPolicy(), Qt.FocusPolicy.StrongFocus)
        win.close()

    def test_normal_note_window_properties(self):
        m = NoteModel(note_type=NOTE_TYPE_NORMAL)
        win = NormalNoteWindow(m, self.nm)
        flags = win.windowFlags()
        self.assertTrue(bool(flags & Qt.WindowType.FramelessWindowHint))
        self.assertTrue(bool(flags & Qt.WindowType.Window))
        # TopBar MUST have close button for normal note
        self.assertIsNotNone(win._content_widget.top_bar.btn_close)
        win.close()

    def test_resize_handle_delta(self):
        m = NoteModel(width=280, height=320)
        target = QWidget()
        target.resize(280, 320)
        rh = ResizeHandle(target, m, self.nm)
        
        # Simulate press
        press = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(5, 5), QPointF(100, 100), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        rh.mousePressEvent(press)
        
        # Simulate move by +40, +50
        move = QMouseEvent(QMouseEvent.Type.MouseMove, QPointF(45, 55), QPointF(140, 150), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        rh.mouseMoveEvent(move)
        
        self.assertEqual(target.size().width(), 320)
        self.assertEqual(target.size().height(), 370)

    def test_settings_popover_escape_dismiss(self):
        m = NoteModel()
        win = QWidget()
        win.show()
        pop = SettingsPopover(win, m, self.nm, QWidget())
        pop.show()
        self.assertTrue(pop.isVisible())
        
        # Send Escape
        esc_ev = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier)
        handled = pop.eventFilter(win, esc_ev)
        self.assertTrue(handled)
        self.assertFalse(pop.isVisible())

    def test_settings_popover_click_outside_dismiss(self):
        m = NoteModel()
        win = QWidget()
        win.show()
        pop = SettingsPopover(win, m, self.nm, QWidget())
        pop.show()
        self.assertTrue(pop.isVisible())
        
        # Click outside on another widget
        other = QWidget()
        click_ev = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(900, 900), QPointF(900, 900), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        pop.eventFilter(other, click_ev)
        self.assertFalse(pop.isVisible())

    def test_settings_popover_qwindow_event_filter(self):
        # Verify filtering events from QWindow objects does not raise TypeError
        from PyQt6.QtGui import QWindow
        m = NoteModel()
        win = QWidget()
        win.show()
        pop = SettingsPopover(win, m, self.nm, QWidget())
        pop.show()
        
        qwin = QWindow()
        click_ev = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(900, 900), QPointF(900, 900), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        pop.eventFilter(qwin, click_ev)
        self.assertFalse(pop.isVisible())

    def test_checklist_toggle_and_click(self):
        m = NoteModel(note_type=NOTE_TYPE_NORMAL)
        win = NormalNoteWindow(m, self.nm)
        te = win._content_widget.text_edit
        te.setPlainText("Buy Milk\nCall Alex")
        
        # Move cursor to first line and toggle checklist
        cursor = te.textCursor()
        cursor.setPosition(2)
        te.setTextCursor(cursor)
        te.toggle_checklist()
        
        self.assertTrue(te.toPlainText().startswith("☐ Buy Milk"))
        
        # Untoggle
        te.toggle_checklist()
        self.assertTrue(te.toPlainText().startswith("Buy Milk"))
        win.close()

    def test_normal_note_collapsible_mini_mode(self):
        m = NoteModel(note_type=NOTE_TYPE_NORMAL, title="Project Specs", width=280, height=320)
        win = NormalNoteWindow(m, self.nm)
        win.show()
        
        self.assertFalse(m.collapsed)
        self.assertTrue(win._content_widget.text_edit.isVisible())
        self.assertFalse(win._content_widget.top_bar.collapsed_title_label.isVisible())
        
        # Collapse
        win.toggle_collapsed()
        self.assertTrue(m.collapsed)
        self.assertFalse(win._content_widget.text_edit.isVisible())
        self.assertTrue(win._content_widget.top_bar.collapsed_title_label.isVisible())
        self.assertEqual(win._content_widget.top_bar.collapsed_title_label.text(), "Project Specs")
        self.assertLess(win.height(), 60)

        # Rename note while rolled up (e.g. from Master Window)
        m.title = "Updated Project Roadmap"
        self.nm.update_note(m)
        self.assertEqual(win._content_widget.top_bar.collapsed_title_label.text(), "Updated Project Roadmap")
        
        # Expand
        win.toggle_collapsed()
        self.assertFalse(m.collapsed)
        self.assertTrue(win._content_widget.text_edit.isVisible())
        self.assertFalse(win._content_widget.top_bar.collapsed_title_label.isVisible())
        self.assertEqual(win.height(), 320)
        win.close()

if __name__ == "__main__":
    unittest.main()
