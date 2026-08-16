from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPolygon, QBrush, QColor

class ResizeHandle(QWidget):
    """A 20x20 drag triangle drawn in the bottom-right corner of the note."""
    def __init__(self, target_window, model, note_manager):
        super().__init__(target_window)
        self._target = target_window
        self._model = model
        self._nm = note_manager
        self.setFixedSize(20, 20)
        self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self._resizing = False
        self._start_global = None
        self._start_size = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        points = [
            QPoint(20, 0),
            QPoint(20, 20),
            QPoint(0, 20)
        ]
        polygon = QPolygon(points)
        painter.setBrush(QBrush(QColor(0, 0, 0, 90)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(polygon)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = True
            self._start_global = event.globalPosition().toPoint()
            self._start_size = self._target.size()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._resizing and self._start_global is not None and self._start_size is not None:
            delta = event.globalPosition().toPoint() - self._start_global
            new_w = max(200, self._start_size.width() + delta.x())
            new_h = max(150, self._start_size.height() + delta.y())
            self._target.resize(new_w, new_h)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self._start_global = None
            self._start_size = None
            event.accept()
