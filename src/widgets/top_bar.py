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
        layout.setContentsMargins(3, 2, 3, 2)
        layout.setSpacing(2)

        self.badge = QLabel("●")
        if self._model.note_type == "emergency":
            self.badge.setStyleSheet("color: #e67e22; font-size: 10px; padding: 0px 2px;")
            self.badge.setToolTip("Sticky Note (Pinned / Always on Top)")
        else:
            self.badge.setStyleSheet("color: #2ecc71; font-size: 10px; padding: 0px 2px;")
            self.badge.setToolTip("Standard Note")

        layout.addWidget(self.badge)

        self.collapsed_title_label = QLabel()
        self.collapsed_title_label.setMinimumWidth(0)
        self.collapsed_title_label.setStyleSheet("color: #333333; font-weight: bold; font-size: 11px; padding-left: 4px;")
        self.collapsed_title_label.hide()
        layout.addWidget(self.collapsed_title_label, stretch=1)

        layout.addStretch()

        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setFixedSize(18, 18)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 9px;
                color: rgba(0, 0, 0, 0.45);
                font-size: 10px;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.09);
                color: rgba(0, 0, 0, 0.85);
            }
        """)
        self.btn_settings.clicked.connect(self._toggle_settings)
        layout.addWidget(self.btn_settings)

        # Emergency notes cannot be closed/deleted from the note itself.
        # Normal notes have a single close button here.
        if self._model.note_type != "emergency":
            self.btn_close = QPushButton("✕")
            self.btn_close.setFixedSize(18, 18)
            self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_close.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 9px;
                    color: rgba(0, 0, 0, 0.45);
                    font-size: 10px;
                }
                QPushButton:hover {
                    background: rgba(231, 76, 60, 0.18);
                    color: #c0392b;
                }
            """)
            self.btn_close.clicked.connect(self._close_window)
            layout.addWidget(self.btn_close)
        else:
            self.btn_close = None

        # Make the top bar a drag target with a hand cursor
        self.setCursor(Qt.CursorShape.SizeAllCursor)

        # Connect note_updated signal to live-update title and color if note is updated
        if hasattr(self._nm, 'note_updated'):
            self._nm.note_updated.connect(self._on_note_updated)

        self._font_color = getattr(self._model, "font_color", "#333333")
        self.set_font_color(self._font_color)

    def set_font_color(self, hex_color: str):
        self._font_color = hex_color
        self.collapsed_title_label.setStyleSheet(f"color: {hex_color}; font-weight: bold; font-size: 11px; padding-left: 4px;")
        self.btn_settings.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 9px;
                color: {hex_color};
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: rgba(128, 128, 128, 0.25);
                color: {hex_color};
            }}
        """)
        if self.btn_close:
            self.btn_close.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 9px;
                    color: {hex_color};
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background: rgba(231, 76, 60, 0.25);
                    color: #e74c3c;
                }}
            """)

    def _on_note_updated(self, model):
        if model.id == self._model.id:
            self._model = model
            if getattr(model, "font_color", None) and model.font_color != self._font_color:
                self.set_font_color(model.font_color)
            if getattr(self._model, "collapsed", False):
                self.set_collapsed_mode(True)

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
            self.window().raise_()
            self.window().activateWindow()
            if hasattr(self._nm, 'bring_to_front'):
                self._nm.bring_to_front(self._model.id)
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
