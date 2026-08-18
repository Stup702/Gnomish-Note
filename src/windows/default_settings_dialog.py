from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QPushButton, QColorDialog,
    QMessageBox, QSlider
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt
from persistence import settings_manager
from widgets.font_selector import CuratedFontComboBox

class DefaultSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Default Note Settings")
        self.setFixedSize(410, 535)
        
        self._current_settings = settings_manager.get_default_settings()
        self._selected_color = self._current_settings["color"]
        self._selected_font_color = self._current_settings["font_color"]

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # -------------------------------------------------------------
        # Section 1: Note Defaults Card
        # -------------------------------------------------------------
        sec1_label = QLabel("NOTE DEFAULTS")
        sec1_label.setObjectName("SectionHeader")
        main_layout.addWidget(sec1_label)

        card1 = QWidget()
        card1.setObjectName("PreferencesCard")
        card1_layout = QVBoxLayout(card1)
        card1_layout.setContentsMargins(12, 10, 12, 10)
        card1_layout.setSpacing(10)

        # Row 1: Font Family
        row_font = QHBoxLayout()
        lbl_font = QLabel("Default Font")
        lbl_font.setObjectName("RowLabel")
        row_font.addWidget(lbl_font)
        row_font.addStretch()
        self.font_combo = CuratedFontComboBox()
        self.font_combo.setObjectName("DarkInput")
        self.font_combo.setFixedWidth(180)
        self.font_combo.set_current_family(self._current_settings["font_family"])
        row_font.addWidget(self.font_combo)
        card1_layout.addLayout(row_font)

        # Row 2: Font Size
        row_size = QHBoxLayout()
        lbl_size = QLabel("Default Font Size")
        lbl_size.setObjectName("RowLabel")
        row_size.addWidget(lbl_size)
        row_size.addStretch()

        btn_minus = QPushButton("−")
        btn_minus.setObjectName("BtnStepper")
        btn_minus.setFixedSize(24, 24)
        btn_minus.clicked.connect(self._decrease_font_size)
        row_size.addWidget(btn_minus)

        self.size_spin = QSpinBox()
        self.size_spin.setObjectName("DarkInput")
        self.size_spin.setRange(6, 72)
        self.size_spin.setFixedWidth(46)
        self.size_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.size_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_spin.setValue(self._current_settings["font_size"])
        row_size.addWidget(self.size_spin)

        btn_plus = QPushButton("+")
        btn_plus.setObjectName("BtnStepper")
        btn_plus.setFixedSize(24, 24)
        btn_plus.clicked.connect(self._increase_font_size)
        row_size.addWidget(btn_plus)

        card1_layout.addLayout(row_size)

        # Row 3: Note Background Color
        row_col = QHBoxLayout()
        lbl_col = QLabel("Default Note Color")
        lbl_col.setObjectName("RowLabel")
        row_col.addWidget(lbl_col)
        row_col.addStretch()
        self.btn_color = QPushButton()
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_color.setFixedSize(50, 24)
        self._update_color_btn(self._selected_color)
        self.btn_color.clicked.connect(self._on_choose_color)
        row_col.addWidget(self.btn_color)
        card1_layout.addLayout(row_col)

        # Row 4: Font Color
        row_fcol = QHBoxLayout()
        lbl_fcol = QLabel("Default Text Color")
        lbl_fcol.setObjectName("RowLabel")
        row_fcol.addWidget(lbl_fcol)
        row_fcol.addStretch()
        self.btn_font_color = QPushButton()
        self.btn_font_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_font_color.setFixedSize(50, 24)
        self._update_font_color_btn(self._selected_font_color)
        self.btn_font_color.clicked.connect(self._on_choose_font_color)
        row_fcol.addWidget(self.btn_font_color)
        card1_layout.addLayout(row_fcol)

        # Row 5: Default Dimensions (W x H)
        row_dim = QHBoxLayout()
        lbl_dim = QLabel("Default Size (W × H)")
        lbl_dim.setObjectName("RowLabel")
        row_dim.addWidget(lbl_dim)
        row_dim.addStretch()
        
        self.width_spin = QSpinBox()
        self.width_spin.setObjectName("DarkInput")
        self.width_spin.setRange(150, 1920)
        self.width_spin.setFixedWidth(64)
        self.width_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.width_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.width_spin.setValue(self._current_settings["width"])
        row_dim.addWidget(self.width_spin)
        
        lbl_x = QLabel("×")
        lbl_x.setStyleSheet("color: #777777; font-size: 13px;")
        row_dim.addWidget(lbl_x)
        
        self.height_spin = QSpinBox()
        self.height_spin.setObjectName("DarkInput")
        self.height_spin.setRange(100, 1080)
        self.height_spin.setFixedWidth(64)
        self.height_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.height_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.height_spin.setValue(self._current_settings["height"])
        row_dim.addWidget(self.height_spin)
        
        # Row 6: Opacity
        row_op = QHBoxLayout()
        lbl_op = QLabel("Default Opacity")
        lbl_op.setObjectName("RowLabel")
        row_op.addWidget(lbl_op)
        row_op.addStretch()

        current_op_val = int(round(self._current_settings.get("opacity", 1.0) * 100))
        self.lbl_op_val = QLabel(f"{current_op_val}%")
        self.lbl_op_val.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: bold; min-width: 32px;")
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(40, 100)
        self.opacity_slider.setValue(current_op_val)
        self.opacity_slider.setFixedWidth(130)
        self.opacity_slider.valueChanged.connect(lambda val: self.lbl_op_val.setText(f"{val}%"))

        row_op.addWidget(self.opacity_slider)
        row_op.addWidget(self.lbl_op_val)
        card1_layout.addLayout(row_op)

        main_layout.addWidget(card1)

        # -------------------------------------------------------------
        # Section 2: System Integration Card
        # -------------------------------------------------------------
        sec2_label = QLabel("SYSTEM INTEGRATION")
        sec2_label.setObjectName("SectionHeader")
        main_layout.addWidget(sec2_label)

        card2 = QWidget()
        card2.setObjectName("PreferencesCard")
        card2_layout = QVBoxLayout(card2)
        card2_layout.setContentsMargins(12, 10, 12, 10)
        card2_layout.setSpacing(10)

        # Row 1: Start on Startup
        row_autostart = QHBoxLayout()
        lbl_autostart = QLabel("Start on Startup")
        lbl_autostart.setObjectName("RowLabel")
        row_autostart.addWidget(lbl_autostart)
        row_autostart.addStretch()

        self.btn_autostart = QPushButton()
        self.btn_autostart.setObjectName("BtnAutostart")
        self.btn_autostart.setFixedHeight(28)
        self.btn_autostart.clicked.connect(self._on_autostart_clicked)
        row_autostart.addWidget(self.btn_autostart)
        self._update_autostart_btn()
        card2_layout.addLayout(row_autostart)

        # Row 2: Alt-Tab Filtering
        row_ext = QHBoxLayout()
        lbl_ext = QLabel("Alt-Tab Filtering")
        lbl_ext.setObjectName("RowLabel")
        row_ext.addWidget(lbl_ext)
        row_ext.addStretch()

        self.btn_ext = QPushButton()
        self.btn_ext.setObjectName("BtnExtAction")
        self.btn_ext.setFixedHeight(28)
        self.btn_ext.clicked.connect(self._on_extension_btn_clicked)
        row_ext.addWidget(self.btn_ext)

        self.btn_ext_uninstall = QPushButton("🗑 Uninstall")
        self.btn_ext_uninstall.setObjectName("BtnExtUninstall")
        self.btn_ext_uninstall.setFixedHeight(28)
        self.btn_ext_uninstall.clicked.connect(self._on_extension_uninstall_clicked)
        row_ext.addWidget(self.btn_ext_uninstall)

        self._update_extension_btn()
        card2_layout.addLayout(row_ext)
        main_layout.addWidget(card2)

        main_layout.addStretch()

        # -------------------------------------------------------------
        # Footer Action Buttons
        # -------------------------------------------------------------
        footer_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset Defaults")
        reset_btn.setObjectName("BtnFlat")
        reset_btn.clicked.connect(self._on_reset)
        footer_layout.addWidget(reset_btn)

        footer_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("BtnPill")
        cancel_btn.clicked.connect(self.reject)
        footer_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Defaults")
        save_btn.setObjectName("BtnSave")
        save_btn.clicked.connect(self._on_save)
        footer_layout.addWidget(save_btn)

        main_layout.addLayout(footer_layout)

        # Apply Libadwaita styling
        self._apply_theme()

    def _apply_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel#SectionHeader {
                color: #9a9996;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
                padding-left: 4px;
            }
            QWidget#PreferencesCard {
                background-color: #262626;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
            QLabel#RowLabel {
                color: #e0e0e0;
                font-size: 12px;
                font-weight: 500;
                background: transparent;
            }
            QComboBox#DarkInput, QSpinBox#DarkInput {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 4px 6px;
                font-size: 12px;
            }
            QSpinBox#DarkInput::up-button, QSpinBox#DarkInput::down-button {
                width: 0px;
                height: 0px;
                border: none;
            }
            QComboBox#DarkInput:focus, QSpinBox#DarkInput:focus {
                border: 1px solid #3584e4;
                background-color: #383838;
            }
            QComboBox#DarkInput::drop-down {
                border: none;
            }
            QPushButton#BtnStepper {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton#BtnStepper:hover {
                background-color: #404040;
            }
            QPushButton#BtnExtAction {
                background-color: #323232;
                color: #2ec27e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 10px;
            }
            QPushButton#BtnExtAction:hover {
                background-color: #3e3e3e;
            }
            QPushButton#BtnAutostart {
                background-color: #323232;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 10px;
            }
            QPushButton#BtnAutostart:hover {
                background-color: #3e3e3e;
            }
            QPushButton#BtnExtUninstall {
                background-color: #3b2222;
                color: #f27979;
                border: 1px solid #703333;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 8px;
            }
            QPushButton#BtnExtUninstall:hover {
                background-color: #4a2828;
                border: 1px solid #e74c3c;
            }
            QPushButton#BtnFlat {
                background: transparent;
                border: none;
                color: #888888;
                font-size: 12px;
                padding: 6px 8px;
            }
            QPushButton#BtnFlat:hover {
                color: #ffffff;
            }
            QPushButton#BtnPill {
                background-color: #2e2e2e;
                color: #cccccc;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
                font-size: 12px;
                padding: 6px 14px;
            }
            QPushButton#BtnPill:hover {
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QPushButton#BtnSave {
                background-color: #2ec27e;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                padding: 6px 16px;
            }
            QPushButton#BtnSave:hover {
                background-color: #26ab6e;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #3e3e3e;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #3584e4;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid rgba(0, 0, 0, 0.2);
                width: 14px;
                margin-top: -5px;
                margin-bottom: -5px;
                border-radius: 7px;
            }
        """)

    def _decrease_font_size(self):
        cur = self.size_spin.value()
        if cur > self.size_spin.minimum():
            self.size_spin.setValue(cur - 1)

    def _increase_font_size(self):
        cur = self.size_spin.value()
        if cur < self.size_spin.maximum():
            self.size_spin.setValue(cur + 1)

    def _update_color_btn(self, color_hex):
        self._selected_color = color_hex
        self.btn_color.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_hex};
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border: 2px solid #3584e4;
            }}
        """)

    def _update_font_color_btn(self, color_hex):
        self._selected_font_color = color_hex
        self.btn_font_color.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_hex};
                border: 1px solid rgba(255, 255, 255, 0.25);
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border: 2px solid #3584e4;
            }}
        """)

    def _on_choose_color(self):
        color = QColorDialog.getColor(
            initial=QColor(self._selected_color),
            parent=self,
            options=QColorDialog.ColorDialogOption.DontUseNativeDialog
        )
        if color.isValid():
            self._update_color_btn(color.name())

    def _on_choose_font_color(self):
        color = QColorDialog.getColor(
            initial=QColor(self._selected_font_color),
            parent=self,
            options=QColorDialog.ColorDialogOption.DontUseNativeDialog
        )
        if color.isValid():
            self._update_font_color_btn(color.name())

    def _on_reset(self):
        settings_manager.reset_default_settings()
        self._current_settings = settings_manager.get_default_settings()
        self.font_combo.set_current_family(self._current_settings["font_family"])
        self.size_spin.setValue(self._current_settings["font_size"])
        self._update_color_btn(self._current_settings["color"])
        self._update_font_color_btn(self._current_settings["font_color"])
        self.width_spin.setValue(self._current_settings["width"])
        self.height_spin.setValue(self._current_settings["height"])
        op_val = int(round(self._current_settings.get("opacity", 1.0) * 100))
        self.opacity_slider.setValue(op_val)
        self.lbl_op_val.setText(f"{op_val}%")

    def _update_autostart_btn(self):
        from core import autostart
        if autostart.is_autostart_enabled():
            self.btn_autostart.setText("✔ Enabled")
            self.btn_autostart.setStyleSheet("color: #2ec27e; font-weight: 600; font-size: 11px;")
            self.btn_autostart.setToolTip("Autostart is enabled. Click to disable starting on system login.")
        else:
            self.btn_autostart.setText("⚡ Enable")
            self.btn_autostart.setStyleSheet("color: #e67e22; font-weight: 600; font-size: 11px;")
            self.btn_autostart.setToolTip("Click to automatically start Gnomish Note on system login.")

    def _on_autostart_clicked(self):
        from core import autostart
        autostart.toggle_autostart()
        self._update_autostart_btn()

    def _update_extension_btn(self):
        from core import extension_installer
        if extension_installer.is_extension_installed():
            self.btn_ext.setText("✔ Installed (Reinstall)")
            self.btn_ext.setStyleSheet("color: #2ec27e; font-weight: 600; font-size: 11px;")
            self.btn_ext_uninstall.show()
        else:
            self.btn_ext.setText("⚡ Install Extension")
            self.btn_ext.setStyleSheet("color: #e67e22; font-weight: 600; font-size: 11px;")
            self.btn_ext_uninstall.hide()

    def _on_extension_btn_clicked(self):
        from core import extension_installer
        extension_installer.install_and_enable_extension(self)
        self._update_extension_btn()
        if self.parent() and hasattr(self.parent(), '_dismiss_banner') and extension_installer.is_extension_installed():
            self.parent()._dismiss_banner()

    def _on_extension_uninstall_clicked(self):
        from core import extension_installer
        extension_installer.uninstall_extension(self)
        self._update_extension_btn()

    def _on_save(self):
        settings_manager.save_default_settings({
            "font_family": self.font_combo.current_family(),
            "font_size": self.size_spin.value(),
            "color": self._selected_color,
            "font_color": self._selected_font_color,
            "width": self.width_spin.value(),
            "height": self.height_spin.value(),
            "opacity": self.opacity_slider.value() / 100.0
        })
        self.accept()
