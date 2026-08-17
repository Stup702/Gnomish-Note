from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QFontComboBox, QSpinBox, QPushButton, QColorDialog,
    QApplication, QWidget
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QEvent

class SettingsPopover(QFrame):
    def __init__(self, note_window, model, note_manager, note_content_widget):
        super().__init__(note_window)
        self.setObjectName("SettingsPopover")
        self.hide()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            #SettingsPopover {
                background-color: #242933;
                border: 1px solid #4c566a;
                border-radius: 8px;
            }
            #SettingsPopover QLabel {
                color: #eceff4;
                font-size: 11px;
                font-weight: bold;
            }
            #SettingsPopover QFontComboBox, #SettingsPopover QSpinBox {
                background-color: #2e3440;
                color: #eceff4;
                border: 1px solid #4c566a;
                border-radius: 4px;
                padding: 2px 4px;
            }
            #SettingsPopover QFontComboBox QAbstractItemView {
                background-color: #2e3440;
                color: #eceff4;
                selection-background-color: #5e81ac;
                selection-color: #ffffff;
            }
        """)

        self._note_window = note_window
        self._model = model
        self._nm = note_manager
        self._note_content_widget = note_content_widget
        self._color_dialog_active = False

        # Debounce timers — prevents rapid repaints while scrolling font list
        self._font_timer = QTimer(self)
        self._font_timer.setSingleShot(True)
        self._font_timer.setInterval(400)
        self._font_timer.timeout.connect(self._apply_font)
        self._pending_font = None

        self._size_timer = QTimer(self)
        self._size_timer.setSingleShot(True)
        self._size_timer.setInterval(300)
        self._size_timer.timeout.connect(self._apply_size)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Font Family
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font:"))
        self.font_combo = QFontComboBox()
        self.font_combo.setMaximumWidth(160)
        self.font_combo.setCurrentFont(QFont(self._model.font_family))
        self.font_combo.currentFontChanged.connect(self._on_font_changed)
        font_layout.addWidget(self.font_combo)
        layout.addLayout(font_layout)

        # Font Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(self._model.font_size)
        self.size_spin.valueChanged.connect(self._on_size_changed)
        size_layout.addWidget(self.size_spin)
        layout.addLayout(size_layout)

        # Note Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Note Color:"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(40, 24)
        self._update_color_btn(self._model.color)
        self.btn_color.clicked.connect(self._on_color_clicked)
        color_layout.addWidget(self.btn_color)
        layout.addLayout(color_layout)

        # Font Color
        font_color_layout = QHBoxLayout()
        font_color_layout.addWidget(QLabel("Font Color:"))
        self.btn_font_color = QPushButton()
        self.btn_font_color.setFixedSize(40, 24)
        self._update_font_color_btn(getattr(self._model, "font_color", "#333333"))
        self.btn_font_color.clicked.connect(self._on_font_color_clicked)
        font_color_layout.addWidget(self.btn_font_color)
        layout.addLayout(font_color_layout)

        self.setFixedWidth(230)
        self.adjustSize()

    def _update_color_btn(self, color_hex):
        self.btn_color.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #999;")

    def _update_font_color_btn(self, color_hex):
        self.btn_font_color.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #999;")

    # --- Font ---
    def _on_font_changed(self, font):
        self._pending_font = font
        self._font_timer.start()

    def _apply_font(self):
        if self._pending_font:
            self._model.font_family = self._pending_font.family()
            self._note_content_widget.set_font(self._model.font_family, self._model.font_size)
            self._nm.update_note(self._model)

    # --- Size ---
    def _on_size_changed(self, size):
        self._size_timer.start()

    def _apply_size(self):
        size = self.size_spin.value()
        self._model.font_size = size
        self._note_content_widget.set_font(self._model.font_family, self._model.font_size)
        self._nm.update_note(self._model)

    # --- Note Color ---
    def _on_color_clicked(self):
        self._color_dialog_active = True
        try:
            color = QColorDialog.getColor(
                initial=QColor(self._model.color),
                parent=self.window(),
                options=QColorDialog.ColorDialogOption.DontUseNativeDialog
            )
            if color.isValid():
                hex_color = color.name()
                self._model.color = hex_color
                self._update_color_btn(hex_color)
                self._note_content_widget.set_color(hex_color)
                self._nm.update_note(self._model)
        finally:
            self._color_dialog_active = False

    # --- Font Color ---
    def _on_font_color_clicked(self):
        self._color_dialog_active = True
        try:
            current_fc = getattr(self._model, "font_color", "#333333")
            color = QColorDialog.getColor(
                initial=QColor(current_fc),
                parent=self.window(),
                options=QColorDialog.ColorDialogOption.DontUseNativeDialog
            )
            if color.isValid():
                hex_color = color.name()
                self._model.font_color = hex_color
                self._update_font_color_btn(hex_color)
                self._note_content_widget.set_font_color(hex_color)
                self._nm.update_note(self._model)
        finally:
            self._color_dialog_active = False

    def showEvent(self, event):
        super().showEvent(event)
        app = QApplication.instance()
        if app:
            app.installEventFilter(self)
        if self.parent():
            self.move(self.parent().width() - self.width() - 10, 40)
            self.raise_()

    def hideEvent(self, event):
        super().hideEvent(event)
        app = QApplication.instance()
        if app:
            app.removeEventFilter(self)

    def eventFilter(self, watched, event):
        if not self.isVisible():
            return False

        # Close on Escape key
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.hide()
                return True

        # Close on clicking anywhere outside this popover
        if event.type() == QEvent.Type.MouseButtonPress:
            if self._color_dialog_active:
                return False
            # Check if clicked inside this popover or any of its child widgets
            if watched == self or self.isAncestorOf(watched):
                return False
            # Check if clicked on a combobox dropdown view belonging to font_combo
            if hasattr(self, 'font_combo') and (watched == self.font_combo.view() or watched == self.font_combo.view().window()):
                return False
            # Check if clicked on the settings button of this note (handled by its own click toggle)
            if (hasattr(self, '_note_content_widget') and
                hasattr(self._note_content_widget, 'top_bar') and
                watched == self._note_content_widget.top_bar.btn_settings):
                return False

            self.hide()
            return False

        return False
