import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, note_manager, main_window):
        self._main_window = main_window
        self._note_manager = note_manager

        icon_path = os.path.join(os.path.dirname(__file__), "..", "icons", "gnomish-note-v4.png")
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            icon = QIcon.fromTheme("accessories-text-editor")
            
        super().__init__(icon, main_window)
        self.setIcon(icon)
        self.setToolTip("Gnomish Note")
        
        menu = QMenu()
        
        act_dash = menu.addAction("Open / Hide Dashboard")
        act_dash.triggered.connect(self._toggle_main_window)
        menu.setDefaultAction(act_dash)

        menu.addSeparator()

        act_sticky = menu.addAction("+ New Sticky Note")
        act_sticky.triggered.connect(lambda: note_manager.create_note(note_type="emergency"))

        act_note = menu.addAction("+ New Note")
        act_note.triggered.connect(lambda: note_manager.create_note(note_type="normal"))

        menu.addSeparator()

        act_show_all = menu.addAction("Show All Notes")
        act_show_all.triggered.connect(note_manager.show_all)

        act_hide_all = menu.addAction("Hide All Notes")
        act_hide_all.triggered.connect(note_manager.hide_all)

        menu.addSeparator()

        act_quit = menu.addAction("Quit Gnomish Note")
        act_quit.triggered.connect(QApplication.quit)
        
        self.setContextMenu(menu)
        self.activated.connect(self._on_activate)

    def _show_main_window(self):
        if self._main_window.isMinimized():
            self._main_window.showNormal()
        self._main_window.show()
        self._main_window.raise_()
        self._main_window.activateWindow()

    def _toggle_main_window(self):
        if self._main_window.isVisible() and not self._main_window.isMinimized():
            self._main_window.hide()
        else:
            self._show_main_window()

    def _on_activate(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self._toggle_main_window()
