from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, note_manager, main_window):
        super().__init__(QIcon.fromTheme("accessories-text-editor"))
        self._main_window = main_window
        
        menu = QMenu()
        menu.addAction("Show Main Window", main_window.show)
        menu.addAction("Show All Notes", note_manager.show_all)
        menu.addAction("Hide All Notes", note_manager.hide_all)
        menu.addSeparator()
        menu.addAction("Quit", QApplication.quit)
        
        self.setContextMenu(menu)
        self.activated.connect(self._on_activate)

    def _on_activate(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._main_window.setVisible(not self._main_window.isVisible())
