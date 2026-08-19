from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class TopBar(QWidget):
    def __init__(self, model, note_manager, settings_popover):
        super().__init__()
        self._model = model
        self._nm = note_manager
        self._settings_popover = settings_popover
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.badge = QLabel()
        if self._model.note_type == "emergency":
            self.badge.setText("⚠ EMERGENCY")
            self.badge.setStyleSheet("color: #d9534f; font-weight: bold; font-size: 11px;")
        else:
            self.badge.setText("● NOTE")
            self.badge.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")

        layout.addWidget(self.badge)

        self.collapsed_title_label = QLabel()
        self.collapsed_title_label.setStyleSheet("color: #333333; font-weight: bold; font-size: 11px; padding-left: 2px;")
        self.collapsed_title_label.hide()
        layout.addWidget(self.collapsed_title_label, stretch=1)

        layout.addStretch()

        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(24, 24)
        self.btn_settings.clicked.connect(self._toggle_settings)
        layout.addWidget(self.btn_settings)

        # Emergency notes cannot be closed/deleted from the note itself.
        # Normal notes have a single close button here.
        if self._model.note_type != "emergency":
            self.btn_close = QPushButton("✕")
            self.btn_close.setFixedSize(24, 24)
            self.btn_close.clicked.connect(self._close_window)
            layout.addWidget(self.btn_close)
        else:
            self.btn_close = None

        # Make the top bar a drag target with a hand cursor
        self.setCursor(Qt.CursorShape.SizeAllCursor)

    def set_collapsed_mode(self, collapsed: bool):
        if collapsed:
            title = getattr(self._model, "title", "").strip()
            if not title:
                from PyQt6.QtGui import QTextDocumentFragment
                clean = QTextDocumentFragment.fromHtml(getattr(self._model, "content_html", "")).toPlainText().strip()
                title = clean[:22].replace('\n', ' ') if clean else "Untitled Note"
            self.collapsed_title_label.setText(title)
            self.collapsed_title_label.show()
        else:
            self.collapsed_title_label.hide()

    def _toggle_settings(self):
        if self._settings_popover:
            self._settings_popover.setVisible(not self._settings_popover.isVisible())
            if self._settings_popover.isVisible():
                self._settings_popover.raise_()

    def _close_window(self):
        win = self.window()
        if hasattr(win, '_model') and win._model:
            win._model.minimized = True
            self._nm.update_note(win._model)
        win.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos') and self._drag_pos is not None:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            if hasattr(win, 'toggle_collapsed'):
                win.toggle_collapsed()
                event.accept()
                return
        super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self.window().activateWindow()
        self.window().raise_()
        event.accept()
