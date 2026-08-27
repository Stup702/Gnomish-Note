from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QColorDialog,
    QApplication, QWidget, QSlider
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QEvent
from widgets.font_selector import CuratedFontComboBox

class SettingsPopover(QFrame):
    def __init__(self, note_window, model, note_manager, note_content_widget):
        super().__init__(note_window)
        self.setObjectName("SettingsPopover")
        self.hide()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            #SettingsPopover {
                background-color: #242424;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
            }
            #SettingsPopover QLabel {
                color: #e0e0e0;
                font-size: 11px;
                font-weight: 600;
            }
            #SettingsPopover QComboBox, #SettingsPopover QSpinBox {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 5px;
                padding: 3px 6px;
                font-size: 11px;
            }
            #SettingsPopover QSpinBox::up-button, #SettingsPopover QSpinBox::down-button {
                width: 0px;
                height: 0px;
                border: none;
            }
            #SettingsPopover QComboBox::drop-down {
                border: none;
            }
            #SettingsPopover QComboBox QAbstractItemView {
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #3584e4;
                selection-color: #ffffff;
                padding: 4px;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 6px;
            }
            QPushButton#BtnStepper {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#BtnStepper:hover {
                background-color: #404040;
            }
            QPushButton#BtnCustomColor {
                background-color: #323232;
                color: #cccccc;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 4px;
                font-size: 10px;
                font-weight: 600;
                padding: 2px 6px;
            }
            QPushButton#BtnCustomColor:hover {
                background-color: #444444;
                color: #ffffff;
            }
            #SettingsPopover QSlider::groove:horizontal {
                height: 4px;
                background: #444444;
                border-radius: 2px;
            }
            #SettingsPopover QSlider::sub-page:horizontal {
                background: #3584e4;
                border-radius: 2px;
            }
            #SettingsPopover QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.2);
                width: 14px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 7px;
            }
        """)

        self._note_window = note_window
        self._model = model
        self._nm = note_manager
        self._note_content_widget = note_content_widget
        self._color_dialog_active = False

        # Debounce timer for size changes
        self._size_timer = QTimer(self)
        self._size_timer.setSingleShot(True)
        self._size_timer.setInterval(300)
        self._size_timer.timeout.connect(self._apply_size)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # 1. Curated Font Family Dropdown
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font:"))
        self.font_combo = CuratedFontComboBox()
        self.font_combo.set_current_family(self._model.font_family)
        self.font_combo.fontChanged.connect(self._on_font_family_changed)
        font_layout.addWidget(self.font_combo, stretch=1)
        layout.addLayout(font_layout)

        # 2. Font Size with [ - ] and [ + ] Stepper Buttons
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        size_layout.addStretch()

        btn_minus = QPushButton("−")
        btn_minus.setObjectName("BtnStepper")
        btn_minus.setFixedSize(22, 22)
        btn_minus.clicked.connect(self._decrease_font_size)
        size_layout.addWidget(btn_minus)

        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setFixedWidth(44)
        self.size_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.size_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_spin.setValue(self._model.font_size)
        self.size_spin.valueChanged.connect(self._on_size_changed)
        size_layout.addWidget(self.size_spin)

        btn_plus = QPushButton("+")
        btn_plus.setObjectName("BtnStepper")
        btn_plus.setFixedSize(22, 22)
        btn_plus.clicked.connect(self._increase_font_size)
        size_layout.addWidget(btn_plus)

        layout.addLayout(size_layout)

        # 3. Note Color Palette & Custom Button
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
        color_layout.setSpacing(6)
        
        color_header = QHBoxLayout()
        color_header.addWidget(QLabel("Note Color:"))
        color_header.addStretch()

        self.btn_color = QPushButton("+ Custom")
        self.btn_color.setObjectName("BtnCustomColor")
        self.btn_color.setToolTip("Open Custom Color Picker...")
        self.btn_color.setFixedHeight(22)
        self.btn_color.clicked.connect(self._on_color_clicked)
        color_header.addWidget(self.btn_color)
        color_layout.addLayout(color_header)

        # Quick Pastel Swatches Row
        swatch_layout = QHBoxLayout()
        swatch_layout.setSpacing(6)
        for hex_col, name in PASTEL_PALETTE:
            btn = QPushButton()
            btn.setFixedSize(20, 20)
            btn.setToolTip(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_col};
                    border: 1px solid rgba(255,255,255,0.25);
                    border-radius: 10px;
                }}
                QPushButton:hover {{
                    border: 2px solid #3584e4;
                }}
            """)
            btn.clicked.connect(lambda checked=False, c=hex_col: self._on_swatch_clicked(c))
            swatch_layout.addWidget(btn)
        swatch_layout.addStretch()
        color_layout.addLayout(swatch_layout)
        layout.addLayout(color_layout)

        # 4. Text Color
        font_color_layout = QHBoxLayout()
        font_color_layout.addWidget(QLabel("Text Color:"))
        font_color_layout.addStretch()

        self.btn_font_color = QPushButton()
        self.btn_font_color.setFixedSize(40, 22)
        self.btn_font_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_font_color_btn(getattr(self._model, "font_color", "#333333"))
        self.btn_font_color.clicked.connect(self._on_font_color_clicked)
        font_color_layout.addWidget(self.btn_font_color)
        layout.addLayout(font_color_layout)

        # 5. Opacity Slider (40% to 100%)
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        
        current_op_val = int(round(getattr(self._model, "opacity", 1.0) * 100))
        self.lbl_opacity_val = QLabel(f"{current_op_val}%")
        self.lbl_opacity_val.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: bold; min-width: 32px;")
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(40, 100)
        self.opacity_slider.setValue(current_op_val)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)

        opacity_layout.addWidget(self.opacity_slider, stretch=1)
        opacity_layout.addWidget(self.lbl_opacity_val)
        layout.addLayout(opacity_layout)

        self.setFixedWidth(240)
        self.adjustSize()

    def _decrease_font_size(self):
        cur = self.size_spin.value()
        if cur > self.size_spin.minimum():
            self.size_spin.setValue(cur - 1)

    def _increase_font_size(self):
        cur = self.size_spin.value()
        if cur < self.size_spin.maximum():
            self.size_spin.setValue(cur + 1)

    def _on_swatch_clicked(self, hex_color):
        self._model.color = hex_color
        self._note_content_widget.set_color(hex_color)
        self._nm.update_note(self._model)

    def _update_color_btn(self, color_hex):
        pass

    def _update_font_color_btn(self, color_hex):
        self.btn_font_color.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_hex};
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border: 2px solid #3584e4;
            }}
        """)

    # --- Font ---
    def _on_font_family_changed(self, font_family: str):
        self._model.font_family = font_family
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

    # --- Opacity ---
    def _on_opacity_changed(self, val: int):
        self.lbl_opacity_val.setText(f"{val}%")
        self._model.opacity = val / 100.0
        if self._note_window:
            self._note_window.setWindowOpacity(self._model.opacity)
        self._nm.update_note(self._model)

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

            # Check if clicked on the settings button of this note
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
