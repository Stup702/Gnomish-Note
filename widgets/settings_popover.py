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
        PASTEL_PALETTE = [
            ("#fdf5c9", "Cream Yellow"),
            ("#d4edda", "Mint Green"),
            ("#d1ecf1", "Sky Blue"),
            ("#f8d7da", "Soft Rose"),
            ("#e2d9f3", "Lavender"),
            ("#fff3cd", "Warm Peach"),
            ("#2e3440", "Nord Dark")
        ]

        color_layout = QVBoxLayout()
        color_layout.setSpacing(4)
        
        color_header = QHBoxLayout()
        color_header.addWidget(QLabel("Note Color:"))
        self.btn_color = QPushButton("🎨")
        self.btn_color.setToolTip("Custom Color Picker...")
        self.btn_color.setFixedSize(26, 22)
        self.btn_color.clicked.connect(self._on_color_clicked)
        color_header.addWidget(self.btn_color)
        color_header.addStretch()
        color_layout.addLayout(color_header)

        # Quick Pastel Swatches Row
        swatch_layout = QHBoxLayout()
        swatch_layout.setSpacing(5)
        for hex_col, name in PASTEL_PALETTE:
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setToolTip(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_col};
                    border: 1px solid rgba(255,255,255,0.2);
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    border: 2px solid #58a6ff;
                }}
            """)
            btn.clicked.connect(lambda checked=False, c=hex_col: self._on_swatch_clicked(c))
            swatch_layout.addWidget(btn)
        swatch_layout.addStretch()
        color_layout.addLayout(swatch_layout)
        layout.addLayout(color_layout)

        # Font Color
        font_color_layout = QHBoxLayout()
        font_color_layout.addWidget(QLabel("Text Color:"))
        self.btn_font_color = QPushButton()
        self.btn_font_color.setFixedSize(36, 22)
        self._update_font_color_btn(getattr(self._model, "font_color", "#333333"))
        self.btn_font_color.clicked.connect(self._on_font_color_clicked)
        font_color_layout.addWidget(self.btn_font_color)
        font_color_layout.addStretch()
        layout.addLayout(font_color_layout)

        self.setFixedWidth(240)
        self.adjustSize()

    def _on_swatch_clicked(self, hex_color):
        self._model.color = hex_color
        self._note_content_widget.set_color(hex_color)
        self._nm.update_note(self._model)

    def _update_color_btn(self, color_hex):
        pass

    def _update_font_color_btn(self, color_hex):
        self.btn_font_color.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #999; border-radius: 3px;")

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

            # Check if watched is this popover or a child widget
            if watched == self or (isinstance(watched, QWidget) and self.isAncestorOf(watched)):
                return False

            # Check if clicked on a combobox dropdown view belonging to font_combo
            if hasattr(self, 'font_combo'):
                try:
                    view = self.font_combo.view()
                    if view and (watched == view or watched == view.window()):
                        return False
                except Exception:
                    pass

            # Check if clicked on the settings button of this note (handled by its own click toggle)
            if (hasattr(self, '_note_content_widget') and
                hasattr(self._note_content_widget, 'top_bar') and
                watched == self._note_content_widget.top_bar.btn_settings):
                return False

            # Check if global click coordinate falls inside the popover rect
            if hasattr(event, 'globalPosition'):
                try:
                    global_pos = event.globalPosition().toPoint()
                    if self.rect().contains(self.mapFromGlobal(global_pos)):
                        return False
                except Exception:
                    pass

            self.hide()
            return False

        return False
