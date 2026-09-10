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
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumSize(100, 60)
        self.setGeometry(self._model.pos_x, self._model.pos_y, self._model.width, self._model.height)
        self.setWindowOpacity(getattr(self._model, "opacity", 1.0))

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        from widgets.note_content import NoteContentWidget
        from widgets.frameless_resizer import FramelessResizer
        self._content_widget = NoteContentWidget(self, self._model, self._note_manager)
        self._layout.addWidget(self._content_widget)
        self._resizer = FramelessResizer(self, self._model, self._note_manager)

    def mousePressEvent(self, event):
        if hasattr(self, '_content_widget') and hasattr(self._content_widget, 'text_edit'):
            self._content_widget.text_edit.setFocus()
        self.raise_()
        self.activateWindow()
        if hasattr(self, '_note_manager') and hasattr(self._note_manager, 'bring_to_front'):
            self._note_manager.bring_to_front(self._model.id)
        super().mousePressEvent(event)

    def toggle_collapsed(self):
        if self._model.collapsed:
            # Expand
            self._model.collapsed = False
            self._content_widget.text_edit.show()
            if hasattr(self._content_widget, 'top_bar'):
                self._content_widget.top_bar.set_collapsed_mode(False)
            if hasattr(self._content_widget, 'resize_handle') and self._content_widget.resize_handle:
                self._content_widget.resize_handle.show()

            # Restore expanded height: check persisted expanded_height, then saved_height, fallback to 320
            target_h = getattr(self._model, 'expanded_height', 0)
            if target_h < 100:
                target_h = getattr(self, '_saved_height', 0)
            if target_h < 100:
                target_h = max(self._model.height, 320)

            self.setMinimumSize(100, 60)
            self.resize(self.width(), target_h)
            self._model.height = target_h
            self._model.expanded_height = target_h
            self._note_manager.update_note(self._model)
        else:
            # Collapse
            current_h = self.height()
            if current_h >= 100:
                self._saved_height = current_h
                self._model.expanded_height = current_h
            elif getattr(self._model, 'expanded_height', 0) < 100:
                self._model.expanded_height = max(self._model.height, 320)

            self._model.collapsed = True
            self._content_widget.text_edit.hide()
            if hasattr(self._content_widget, 'top_bar'):
                self._content_widget.top_bar.set_collapsed_mode(True)
            if hasattr(self._content_widget, 'resize_handle') and self._content_widget.resize_handle:
                self._content_widget.resize_handle.hide()
            min_h = self._content_widget.top_bar.sizeHint().height() + 6
            self.setMinimumSize(100, min_h)
            self.resize(self.width(), min_h)
            self._note_manager.update_note(self._model)

    def showEvent(self, event):
        self._restoring = True
        super().showEvent(event)
        self.move(self._model.pos_x, self._model.pos_y)
        if self._model.collapsed:
            self._content_widget.text_edit.hide()
            if hasattr(self._content_widget, 'top_bar'):
                self._content_widget.top_bar.set_collapsed_mode(True)
            if hasattr(self._content_widget, 'resize_handle') and self._content_widget.resize_handle:
                self._content_widget.resize_handle.hide()
            min_h = self._content_widget.top_bar.sizeHint().height() + 6
            self.setMinimumSize(100, min_h)
            self.resize(self._model.width, min_h)
        else:
            if hasattr(self._content_widget, 'top_bar'):
                self._content_widget.top_bar.set_collapsed_mode(False)
            target_h = self._model.expanded_height if getattr(self._model, 'expanded_height', 0) >= 100 else self._model.height
            self.resize(self._model.width, target_h)
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
        if not self._model.collapsed:
            self._model.height = event.size().height()
            self._model.expanded_height = event.size().height()
        self._note_manager.update_note(self._model)

    def closeEvent(self, event):
        event.accept()
        self.hide()
