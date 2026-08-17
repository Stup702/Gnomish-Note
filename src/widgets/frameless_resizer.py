from PyQt6.QtCore import QObject, QEvent, Qt, QPoint
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QGuiApplication

EDGE_NONE = 0
EDGE_TOP = 1
EDGE_BOTTOM = 2
EDGE_LEFT = 4
EDGE_RIGHT = 8

class FramelessResizer(QObject):
    """
    Installs mouse tracking and 8-direction edge/corner resizing
    on any frameless QWidget and all its descendants.
    """
    def __init__(self, target_window: QWidget, model, note_manager, margin: int = 8, corner_margin: int = 20, min_w: int = 200, min_h: int = 150):
        super().__init__(target_window)
        self._target = target_window
        self._model = model
        self._nm = note_manager
        self._margin = margin
        self._corner_margin = corner_margin
        self._min_w = min_w
        self._min_h = min_h

        self._active_zone = EDGE_NONE
        self._start_global = None
        self._start_geometry = None
        self._cursor_overridden = False
        self._current_cursor = None

        self._attach_recursively(self._target)

    def _attach_recursively(self, widget: QWidget):
        if not isinstance(widget, QWidget):
            return
        widget.setMouseTracking(True)
        widget.installEventFilter(self)
        for child in widget.findChildren(QWidget):
            child.setMouseTracking(True)
            child.installEventFilter(self)

    def get_zone_at(self, pos: QPoint) -> int:
        x, y = pos.x(), pos.y()
        w, h = self._target.width(), self._target.height()
        em = self._margin
        cm = self._corner_margin

        # If outside window rect entirely, no zone
        if x < 0 or y < 0 or x > w or y > h:
            return EDGE_NONE

        # 1. Check generous corner zones (20px wiggle room)
        if x <= cm and y <= cm:
            return EDGE_TOP | EDGE_LEFT
        if x >= w - cm and y <= cm:
            return EDGE_TOP | EDGE_RIGHT
        if x <= cm and y >= h - cm:
            return EDGE_BOTTOM | EDGE_LEFT
        if x >= w - cm and y >= h - cm:
            return EDGE_BOTTOM | EDGE_RIGHT

        # 2. Check flat edge zones (8px margin)
        zone = EDGE_NONE
        if y <= em:
            zone |= EDGE_TOP
        elif y >= h - em:
            zone |= EDGE_BOTTOM

        if x <= em:
            zone |= EDGE_LEFT
        elif x >= w - em:
            zone |= EDGE_RIGHT

        return zone

    def get_cursor_for_zone(self, zone: int):
        if zone in (EDGE_TOP | EDGE_LEFT, EDGE_BOTTOM | EDGE_RIGHT):
            return Qt.CursorShape.SizeFDiagCursor
        elif zone in (EDGE_TOP | EDGE_RIGHT, EDGE_BOTTOM | EDGE_LEFT):
            return Qt.CursorShape.SizeBDiagCursor
        elif zone in (EDGE_TOP, EDGE_BOTTOM):
            return Qt.CursorShape.SizeVerCursor
        elif zone in (EDGE_LEFT, EDGE_RIGHT):
            return Qt.CursorShape.SizeHorCursor
        return None

    def _set_override_cursor(self, cursor):
        if not self._cursor_overridden:
            QGuiApplication.setOverrideCursor(cursor)
            self._cursor_overridden = True
            self._current_cursor = cursor
        elif self._current_cursor != cursor:
            QGuiApplication.changeOverrideCursor(cursor)
            self._current_cursor = cursor

    def _restore_override_cursor(self):
        if self._cursor_overridden:
            QGuiApplication.restoreOverrideCursor()
            self._cursor_overridden = False
            self._current_cursor = None

    def eventFilter(self, watched, event):
        try:
            if not isinstance(watched, QWidget):
                return super().eventFilter(watched, event)

            if watched != self._target and not self._target.isAncestorOf(watched):
                return super().eventFilter(watched, event)
        except (RuntimeError, Exception):
            return super().eventFilter(watched, event)

        try:
            event_type = event.type()

            # Handle mouse movement
            if event_type in (QEvent.Type.MouseMove, QEvent.Type.HoverMove):
                if self._active_zone != EDGE_NONE:
                    self._handle_resize(event)
                    return True
                else:
                    if hasattr(event, 'globalPosition'):
                        global_pt = event.globalPosition().toPoint()
                    else:
                        global_pt = watched.mapToGlobal(event.pos())

                    pos_in_target = self._target.mapFromGlobal(global_pt)
                    zone = self.get_zone_at(pos_in_target)
                    cursor = self.get_cursor_for_zone(zone)

                    if cursor is not None:
                        self._set_override_cursor(cursor)
                    else:
                        self._restore_override_cursor()

            # Handle mouse press
            elif event_type == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    if hasattr(event, 'globalPosition'):
                        global_pt = event.globalPosition().toPoint()
                    else:
                        global_pt = watched.mapToGlobal(event.pos())

                    pos_in_target = self._target.mapFromGlobal(global_pt)
                    zone = self.get_zone_at(pos_in_target)
                    if zone != EDGE_NONE:
                        self._active_zone = zone
                        self._start_global = global_pt
                        self._start_geometry = self._target.geometry()
                        return True

            # Handle mouse release
            elif event_type == QEvent.Type.MouseButtonRelease:
                if self._active_zone != EDGE_NONE:
                    self._active_zone = EDGE_NONE
                    self._start_global = None
                    self._start_geometry = None
                    self._model.pos_x = self._target.pos().x()
                    self._model.pos_y = self._target.pos().y()
                    self._model.width = self._target.width()
                    self._model.height = self._target.height()
                    self._nm.update_note(self._model)
                    self._restore_override_cursor()
                    return True

            # Handle leave or hide
            elif event_type in (QEvent.Type.Leave, QEvent.Type.Hide):
                if self._active_zone == EDGE_NONE:
                    self._restore_override_cursor()

            # Dynamic child discovery
            elif event_type == QEvent.Type.ChildAdded:
                child = getattr(event, 'child', lambda: None)()
                if isinstance(child, QWidget):
                    child.setMouseTracking(True)
                    child.installEventFilter(self)
        except (RuntimeError, Exception):
            return super().eventFilter(watched, event)

        return super().eventFilter(watched, event)

    def _handle_resize(self, event):
        if not self._start_global or not self._start_geometry:
            return

        if hasattr(event, 'globalPosition'):
            cur_global = event.globalPosition().toPoint()
        else:
            cur_global = self._target.mapToGlobal(event.pos())

        dx = cur_global.x() - self._start_global.x()
        dy = cur_global.y() - self._start_global.y()

        min_w = self._min_w
        min_h = self._min_h
        if getattr(self._model, 'collapsed', False):
            if hasattr(self._target, '_content_widget') and hasattr(self._target._content_widget, 'top_bar'):
                min_h = self._target._content_widget.top_bar.sizeHint().height() + 8

        start_x = self._start_geometry.x()
        start_y = self._start_geometry.y()
        start_w = self._start_geometry.width()
        start_h = self._start_geometry.height()

        new_x, new_y, new_w, new_h = start_x, start_y, start_w, start_h

        if self._active_zone & EDGE_RIGHT:
            new_w = max(min_w, start_w + dx)
        elif self._active_zone & EDGE_LEFT:
            calc_w = start_w - dx
            new_w = max(min_w, calc_w)
            new_x = start_x + (start_w - new_w)

        if self._active_zone & EDGE_BOTTOM:
            new_h = max(min_h, start_h + dy)
        elif self._active_zone & EDGE_TOP:
            calc_h = start_h - dy
            new_h = max(min_h, calc_h)
            new_y = start_y + (start_h - new_h)

        self._target.setGeometry(new_x, new_y, new_w, new_h)
