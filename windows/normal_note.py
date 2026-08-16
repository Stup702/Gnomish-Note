from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QColor

class NormalNoteWindow(QWidget):
    def __init__(self, model, note_manager):
        super().__init__()
        self._model = model
        self._note_manager = note_manager
        self._restoring = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(200, 150)
        self.setGeometry(self._model.pos_x, self._model.pos_y, self._model.width, self._model.height)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        from widgets.note_content import NoteContentWidget
        self._content_widget = NoteContentWidget(self, self._model, self._note_manager)
        self._layout.addWidget(self._content_widget)

    def toggle_collapsed(self):
        if self._model.collapsed:
            # Expand
            self._model.collapsed = False
            self._content_widget.text_edit.show()
            if hasattr(self._content_widget, 'resize_handle') and self._content_widget.resize_handle:
                self._content_widget.resize_handle.show()
            saved_h = getattr(self, '_saved_height', max(150, self._model.height))
            self.setMinimumSize(200, 150)
            self.resize(self.width(), saved_h)
            self._model.height = saved_h
            self._note_manager.update_note(self._model)
        else:
            # Collapse
            self._saved_height = self.height()
            self._model.collapsed = True
            self._content_widget.text_edit.hide()
            if hasattr(self._content_widget, 'resize_handle') and self._content_widget.resize_handle:
                self._content_widget.resize_handle.hide()
            min_h = self._content_widget.top_bar.sizeHint().height() + 8
            self.setMinimumSize(200, min_h)
            self.resize(self.width(), min_h)
            self._note_manager.update_note(self._model)

    def showEvent(self, event):
        self._restoring = True
        super().showEvent(event)
        self.move(self._model.pos_x, self._model.pos_y)
        if self._model.collapsed:
            self._content_widget.text_edit.hide()
            if hasattr(self._content_widget, 'resize_handle') and self._content_widget.resize_handle:
                self._content_widget.resize_handle.hide()
            min_h = self._content_widget.top_bar.sizeHint().height() + 8
            self.setMinimumSize(200, min_h)
            self.resize(self._model.width, min_h)
        else:
            self.resize(self._model.width, self._model.height)
            if hasattr(self, '_content_widget') and self._content_widget.resize_handle:
                rh = self._content_widget.resize_handle
                rh.move(self.width() - rh.width() - 2, self.height() - rh.height() - 2)
                rh.raise_()
        self._restoring = False

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            self._model.minimized = self.isMinimized()
            self._note_manager.update_note(self._model)

    def moveEvent(self, event):
        super().moveEvent(event)
        if getattr(self, '_restoring', False):
            return
        self._model.pos_x = self.pos().x()
        self._model.pos_y = self.pos().y()
        self._note_manager.update_note(self._model)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_content_widget') and self._content_widget.resize_handle:
            rh = self._content_widget.resize_handle
            rh.move(self.width() - rh.width() - 2, self.height() - rh.height() - 2)
            rh.raise_()
        if getattr(self, '_restoring', False):
            return
        self._model.width = event.size().width()
        self._model.height = event.size().height()
        self._note_manager.update_note(self._model)

    def closeEvent(self, event):
        event.accept()
        self.hide()
