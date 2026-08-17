from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt, QTimer
from .top_bar import TopBar
from .resize_handle import ResizeHandle
from .settings_popover import SettingsPopover

class NoteContentWidget(QWidget):
    def __init__(self, target_window, model, note_manager):
        super().__init__(target_window)
        self._target = target_window
        self._model = model
        self._nm = note_manager

        # Debounce timer for text changes — initialize early before any signal triggers
        self._text_timer = QTimer(self)
        self._text_timer.setSingleShot(True)
        self._text_timer.setInterval(500)
        self._text_timer.timeout.connect(self._save_text)
        
        self.layout = QVBoxLayout(self)
        # Emergency window already sets 20px margins for shadow space;
        # normal notes get small internal padding for the native frame border.
        if self._model.note_type == "emergency":
            self.layout.setContentsMargins(0, 0, 0, 0)
        else:
            self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)
        
        # We need a container for the actual note background so that shadow doesn't affect the widget background
        self.container = QWidget()
        self.container.setObjectName("NoteContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.settings_popover = SettingsPopover(self._target, self._model, self._nm, self)
        self.top_bar = TopBar(self._model, self._nm, self.settings_popover)
        container_layout.addWidget(self.top_bar)
        
        self.text_edit = QTextEdit()
        self.text_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_edit.setPlaceholderText("Write your note here...")
        self.text_edit.setStyleSheet("QTextEdit { border: none; background: transparent; }")
        
        # Set initial content and font
        if self._model.content_html:
            self.set_content_html(self._model.content_html)
        self.set_font(self._model.font_family, self._model.font_size)
        self.set_color(self._model.color)
        self.set_font_color(getattr(self._model, "font_color", "#333333"))

        self.text_edit.textChanged.connect(self._on_text_changed)
        
        container_layout.addWidget(self.text_edit)
        self.layout.addWidget(self.container)
        
        # Resize handle on bottom-right corner for all notes
        self.resize_handle = ResizeHandle(self._target, self._model, self._nm)
        
        self._update_title()

    def set_font_color(self, hex_color):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(hex_color))
        
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(fmt)
        
        self.text_edit.setCurrentCharFormat(fmt)
        self.text_edit.setStyleSheet(f"QTextEdit {{ border: none; background: transparent; color: {hex_color}; }}")

    def set_color(self, hex_color):
        border_color = "#f5a623" if self._model.note_type == "emergency" else "#e1d599"
        self.container.setStyleSheet(f"""
            #NoteContainer {{
                background-color: {hex_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
        """)
        
    def set_font(self, family, size):
        font = QFont(family, size)
        self.text_edit.setFont(font)
        self.text_edit.document().setDefaultFont(font)
        self.text_edit.setFontPointSize(size)
        self.text_edit.setFontFamily(family)
        self.text_edit.setCurrentFont(font)
        
        fmt = QTextCharFormat()
        fmt.setFontFamily(family)
        fmt.setFontPointSize(size)
        fc = getattr(self._model, "font_color", "#333333")
        fmt.setForeground(QColor(fc))
        
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.mergeCharFormat(fmt)
        
        self.text_edit.setCurrentCharFormat(fmt)
        
    def get_content_html(self):
        return self.text_edit.toHtml()
        
    def set_content_html(self, html):
        self.text_edit.setHtml(html)
        
    def _on_text_changed(self):
        self._text_timer.start()
        self._update_title()
        
    def _save_text(self):
        self._model.content_html = self.get_content_html()
        self._nm.update_note(self._model)
        
    def _update_title(self):
        plain_text = self.text_edit.toPlainText()
        preview = plain_text[:20].replace('\n', ' ') or 'New Note'
        if self._model.note_type == "emergency":
            self._target.setWindowTitle(f"[Note] Emergency - {preview}")
        else:
            self._target.setWindowTitle(f"[Note] {preview}")
            

