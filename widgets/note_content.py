from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMenu
from PyQt6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor, QAction
from PyQt6.QtCore import Qt, QTimer
from .top_bar import TopBar
from .resize_handle import ResizeHandle
from .settings_popover import SettingsPopover

class NoteTextEdit(QTextEdit):
    """Custom QTextEdit with interactive checklists, right-click context menu, and Smart Enter."""
    def toggle_checklist(self):
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        text = cursor.selectedText()
        cursor.beginEditBlock()
        if text.startswith("☐ "):
            cursor.removeSelectedText()
            cursor.insertText(text[2:])
        elif text.startswith("☑ "):
            cursor.removeSelectedText()
            cursor.insertText(text[2:])
            # Remove strikethrough if present
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            fmt = QTextCharFormat()
            fmt.setFontStrikeOut(False)
            cursor.mergeCharFormat(fmt)
        else:
            cursor.removeSelectedText()
            cursor.insertText("☐ " + text)
        cursor.endEditBlock()

    def toggle_strikethrough(self):
        cursor = self.textCursor()
        fmt = cursor.charFormat()
        new_fmt = QTextCharFormat()
        new_fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        cursor.mergeCharFormat(new_fmt)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        act_check = QAction("☑ Toggle Checklist", self)
        act_check.setShortcut("Ctrl+Shift+C")
        act_check.triggered.connect(self.toggle_checklist)
        menu.addAction(act_check)

        act_strike = QAction("<s> Strikethrough", self)
        act_strike.setShortcut("Ctrl+Shift+X")
        act_strike.triggered.connect(self.toggle_strikethrough)
        menu.addAction(act_strike)

        menu.exec(event.globalPos())

    def keyPressEvent(self, event):
        # Shortcut: Ctrl+Shift+C -> toggle checklist
        if (event.key() == Qt.Key.Key_C and
            event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
            self.toggle_checklist()
            event.accept()
            return

        # Shortcut: Ctrl+Shift+X -> toggle strikethrough
        if (event.key() == Qt.Key.Key_X and
            event.modifiers() == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)):
            self.toggle_strikethrough()
            event.accept()
            return

        # Smart Enter for checklists
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()
            
            # If current line is an empty checklist item, clear the checkbox to exit checklist mode
            if text in ("☐ ", "☑ ", "☐", "☑"):
                cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
                cursor.removeSelectedText()
                event.accept()
                return

            # If current line is a checklist item, auto-insert new checkbox on next line
            if text.startswith("☐ ") or text.startswith("☑ "):
                cursor.insertText("\n☐ ")
                # Reset strikethrough for new line
                fmt = QTextCharFormat()
                fmt.setFontStrikeOut(False)
                cursor.mergeCharFormat(fmt)
                self.setTextCursor(cursor)
                event.accept()
                return

        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            block = cursor.block()
            block_text = block.text()
            pos_in_block = cursor.positionInBlock()

            # If clicking the checkbox prefix (first 2-3 characters)
            if pos_in_block <= 2:
                if block_text.startswith("☐ "):
                    # Check the item and strike through text
                    c = QTextCursor(block)
                    c.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 2)
                    c.insertText("☑ ")
                    c.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                    fmt = QTextCharFormat()
                    fmt.setFontStrikeOut(True)
                    c.mergeCharFormat(fmt)
                    event.accept()
                    return
                elif block_text.startswith("☑ "):
                    # Uncheck the item and remove strikethrough
                    c = QTextCursor(block)
                    c.movePosition(QTextCursor.MoveOperation.StartOfBlock)
                    c.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, 2)
                    c.insertText("☐ ")
                    c.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
                    fmt = QTextCharFormat()
                    fmt.setFontStrikeOut(False)
                    c.mergeCharFormat(fmt)
                    event.accept()
                    return

        super().mousePressEvent(event)

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
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(0)
        
        self.container = QWidget()
        self.container.setObjectName("NoteContainer")
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        self.settings_popover = SettingsPopover(self._target, self._model, self._nm, self)
        self.top_bar = TopBar(self._model, self._nm, self.settings_popover)
        container_layout.addWidget(self.top_bar)
        
        self.text_edit = NoteTextEdit()
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
            

