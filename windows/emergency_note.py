from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

class EmergencyNoteWindow(QWidget):
    def __init__(self, model, note_manager):
        super().__init__()
        self._model = model
        self._note_manager = note_manager
        self._restoring = False
        self._drag_pos = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.ToolTip
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(200, 150)
        self.setGeometry(self._model.pos_x, self._model.pos_y, self._model.width, self._model.height)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        from widgets.note_content import NoteContentWidget
        self._content_widget = NoteContentWidget(self, self._model, self._note_manager)
        self._layout.addWidget(self._content_widget)

    def showEvent(self, event):
        self._restoring = True
        super().showEvent(event)
        if hasattr(self, '_content_widget') and self._content_widget.resize_handle:
            rh = self._content_widget.resize_handle
            rh.move(self.width() - rh.width() - 2, self.height() - rh.height() - 2)
            rh.raise_()
        self._restoring = False

    def moveEvent(self, event):
        super().moveEvent(event)
        if self._restoring:
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
        if self._restoring:
            return
        self._model.width = event.size().width()
        self._model.height = event.size().height()
        self._note_manager.update_note(self._model)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
