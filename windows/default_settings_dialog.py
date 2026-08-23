from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
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
        self.setFixedSize(360, 360)
        
        self._current_settings = settings_manager.get_default_settings()
        self._selected_color = self._current_settings["color"]
        self._selected_font_color = self._current_settings["font_color"]

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header description
        desc = QLabel("Configure global default styles and system integrations:")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)

        # 1. Font Family
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Default Font:"))
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont(self._current_settings["font_family"]))
        font_layout.addWidget(self.font_combo, stretch=1)
        layout.addLayout(font_layout)

        # 2. Font Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Default Font Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(self._current_settings["font_size"])
        size_layout.addWidget(self.size_spin, stretch=1)
        layout.addLayout(size_layout)

        # 3. Note Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Default Note Color:"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(40, 24)
        self._update_color_btn(self._selected_color)
        self.btn_color.clicked.connect(self._on_choose_color)
        color_layout.addWidget(self.btn_color)
        color_layout.addStretch()
        layout.addLayout(color_layout)

        # 4. Font Color
        font_color_layout = QHBoxLayout()
        font_color_layout.addWidget(QLabel("Default Text Color:"))
        self.btn_font_color = QPushButton()
        self.btn_font_color.setFixedSize(40, 24)
        self._update_font_color_btn(self._selected_font_color)
        self.btn_font_color.clicked.connect(self._on_choose_font_color)
        font_color_layout.addWidget(self.btn_font_color)
        font_color_layout.addStretch()
        layout.addLayout(font_color_layout)

        # 5. Default Dimensions
        dim_layout = QHBoxLayout()
        dim_layout.addWidget(QLabel("Default Size (W x H):"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(150, 1920)
        self.width_spin.setValue(self._current_settings["width"])
        dim_layout.addWidget(self.width_spin)
        
        dim_layout.addWidget(QLabel("x"))
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(100, 1080)
        self.height_spin.setValue(self._current_settings["height"])
        dim_layout.addWidget(self.height_spin)
        layout.addLayout(dim_layout)

        # 6. GNOME Shell Integration Extension
        ext_layout = QHBoxLayout()
        ext_layout.addWidget(QLabel("Alt-Tab Extension:"))
        
        self.btn_ext = QPushButton()
        self.btn_ext.setFixedHeight(26)
        self.btn_ext.clicked.connect(self._on_extension_btn_clicked)
        ext_layout.addWidget(self.btn_ext, stretch=1)

        self.btn_ext_uninstall = QPushButton("🗑 Uninstall")
        self.btn_ext_uninstall.setFixedHeight(26)
        self.btn_ext_uninstall.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 11px;")
        self.btn_ext_uninstall.clicked.connect(self._on_extension_uninstall_clicked)
        ext_layout.addWidget(self.btn_ext_uninstall)

        self._update_extension_btn()
        layout.addLayout(ext_layout)

        layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset Defaults")
        reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Defaults")
        save_btn.setStyleSheet("font-weight: bold; background-color: #27ae60; color: white;")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _update_color_btn(self, color_hex):
        self._selected_color = color_hex
        self.btn_color.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #888; border-radius: 3px;")

    def _update_font_color_btn(self, color_hex):
        self._selected_font_color = color_hex
        self.btn_font_color.setStyleSheet(f"background-color: {color_hex}; border: 1px solid #888; border-radius: 3px;")

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
            self.btn_ext.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
            self.btn_ext_uninstall.show()
        else:
            self.btn_ext.setText("⚡ Install Extension")
            self.btn_ext.setStyleSheet("color: #d08770; font-weight: bold; font-size: 11px;")
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
