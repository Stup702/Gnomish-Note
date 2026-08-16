from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFontComboBox, QSpinBox, QPushButton, QColorDialog,
    QMessageBox
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt
from persistence import settings_manager

class DefaultSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Default Note Settings")
        self.setFixedSize(410, 500)
        
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
        self.font_combo = QFontComboBox()
        self.font_combo.setObjectName("DarkInput")
        self.font_combo.setFixedWidth(180)
        self.font_combo.setCurrentFont(QFont(self._current_settings["font_family"]))
        row_font.addWidget(self.font_combo)
        card1_layout.addLayout(row_font)

        # Row 2: Font Size
        row_size = QHBoxLayout()
        lbl_size = QLabel("Default Font Size")
        lbl_size.setObjectName("RowLabel")
        row_size.addWidget(lbl_size)
        row_size.addStretch()
        self.size_spin = QSpinBox()
        self.size_spin.setObjectName("DarkInput")
        self.size_spin.setRange(6, 72)
        self.size_spin.setFixedWidth(90)
        self.size_spin.setValue(self._current_settings["font_size"])
        row_size.addWidget(self.size_spin)
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
        self.width_spin.setFixedWidth(75)
        self.width_spin.setValue(self._current_settings["width"])
        row_dim.addWidget(self.width_spin)
        
        lbl_x = QLabel("×")
        lbl_x.setStyleSheet("color: #777777; font-size: 13px;")
        row_dim.addWidget(lbl_x)
        
        self.height_spin = QSpinBox()
        self.height_spin.setObjectName("DarkInput")
        self.height_spin.setRange(100, 1080)
        self.height_spin.setFixedWidth(75)
        self.height_spin.setValue(self._current_settings["height"])
        row_dim.addWidget(self.height_spin)
        
        card1_layout.addLayout(row_dim)
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
        card2_layout.setSpacing(8)

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
            QFontComboBox#DarkInput, QSpinBox#DarkInput {
                background-color: #323232;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 4px 6px;
                font-size: 12px;
            }
            QFontComboBox#DarkInput:focus, QSpinBox#DarkInput:focus {
                border: 1px solid #3584e4;
                background-color: #383838;
            }
            QFontComboBox#DarkInput::drop-down {
                border: none;
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
        """)

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
        self.font_combo.setCurrentFont(QFont(self._current_settings["font_family"]))
        self.size_spin.setValue(self._current_settings["font_size"])
        self._update_color_btn(self._current_settings["color"])
        self._update_font_color_btn(self._current_settings["font_color"])
        self.width_spin.setValue(self._current_settings["width"])
        self.height_spin.setValue(self._current_settings["height"])

    def _update_extension_btn(self):
        import extension_installer
        if extension_installer.is_extension_installed():
            self.btn_ext.setText("✔ Installed (Reinstall)")
            self.btn_ext.setStyleSheet("color: #2ec27e; font-weight: 600; font-size: 11px;")
            self.btn_ext_uninstall.show()
        else:
            self.btn_ext.setText("⚡ Install Extension")
            self.btn_ext.setStyleSheet("color: #e67e22; font-weight: 600; font-size: 11px;")
            self.btn_ext_uninstall.hide()

    def _on_extension_btn_clicked(self):
        import extension_installer
        extension_installer.install_and_enable_extension(self)
        self._update_extension_btn()
        if self.parent() and hasattr(self.parent(), '_dismiss_banner') and extension_installer.is_extension_installed():
            self.parent()._dismiss_banner()

    def _on_extension_uninstall_clicked(self):
        import extension_installer
        extension_installer.uninstall_extension(self)
        self._update_extension_btn()

    def _on_save(self):
        settings_manager.save_default_settings({
            "font_family": self.font_combo.currentFont().family(),
            "font_size": self.size_spin.value(),
            "color": self._selected_color,
            "font_color": self._selected_font_color,
            "width": self.width_spin.value(),
            "height": self.height_spin.value()
        })
        self.accept()
