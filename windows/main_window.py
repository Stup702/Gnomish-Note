from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QTextDocumentFragment
import sys
import extension_installer

class NoteListItem(QWidget):
    def __init__(self, model, note_manager):
        super().__init__()
        self._model = model
        self._note_manager = note_manager
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(6)
        
        # Type icon/label badge
        self.type_label = QLabel()
        if model.note_type == "emergency":
            self.type_label.setText("●")
            self.type_label.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 14px;")
            self.type_label.setToolTip("Always-on-top Sticky Note")
        else:
            self.type_label.setText("●")
            self.type_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")
            self.type_label.setToolTip("Standard Note")
        layout.addWidget(self.type_label)
        
        self.preview_label = QLabel()
        layout.addWidget(self.preview_label, stretch=1)
        self._update_text()
        
        # Rename button
        rename_btn = QPushButton("✏")
        rename_btn.setToolTip("Rename Note")
        rename_btn.setFixedSize(28, 28)
        rename_btn.clicked.connect(self._on_rename)
        layout.addWidget(rename_btn)

        # Delete button
        del_btn = QPushButton("🗑")
        del_btn.setToolTip("Delete Note")
        del_btn.setFixedSize(28, 28)
        del_btn.clicked.connect(self._on_delete)
        layout.addWidget(del_btn)

        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._open_note()
        super().mousePressEvent(event)

    def _open_note(self):
        window = self._note_manager._windows.get(self._model.id)
        if not window:
            self._note_manager._create_window_for_model(self._model)
            window = self._note_manager._windows.get(self._model.id)
        if window:
            self._model.minimized = False
            self._note_manager.update_note(self._model)
            if hasattr(window, 'isMinimized') and window.isMinimized():
                window.showNormal()
            window.show()
            window.raise_()
            window.activateWindow()

    def _on_rename(self):
        from PyQt6.QtWidgets import QInputDialog
        current_title = getattr(self._model, "title", "")
        new_title, ok = QInputDialog.getText(
            self.window(),
            "Rename Note",
            "Enter name for this note:",
            text=current_title
        )
        if ok:
            self._model.title = new_title.strip()
            self._note_manager.update_note(self._model)
            self.update_model(self._model)

    def _on_delete(self):
        self._note_manager.delete_note(self._model.id)
        
    def _update_text(self):
        title = getattr(self._model, "title", "").strip()
        content = getattr(self._model, "content_html", "")
        clean_text = QTextDocumentFragment.fromHtml(content).toPlainText().strip()
        preview = clean_text[:35].replace('\n', ' ') if clean_text else ""
        
        if title and preview:
            self.preview_label.setText(f"<b>{title}</b> — <span style='color: #888;'>{preview}</span>")
        elif title:
            self.preview_label.setText(f"<b>{title}</b>")
        elif preview:
            self.preview_label.setText(preview)
        else:
            self.preview_label.setText("Empty Note")

    def update_model(self, model):
        self._model = model
        if model.note_type == "emergency":
            self.type_label.setText("●")
            self.type_label.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 14px;")
            self.type_label.setToolTip("Always-on-top Sticky Note")
        else:
            self.type_label.setText("●")
            self.type_label.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 14px;")
            self.type_label.setToolTip("Standard Note")
            
        self._update_text()

class MainWindow(QMainWindow):
    def __init__(self, note_manager):
        super().__init__()
        self._note_manager = note_manager
        
        self.setWindowTitle("Sticky Notes")
        self.resize(400, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Extension Banner — only show if extension is not installed
        self.settings = QSettings("gnome-sticky-notes", "main")
        if (not extension_installer.is_extension_installed() and
                not self.settings.value("extension_banner_dismissed", False, type=bool)):
            self.banner_layout = QHBoxLayout()
            self.banner_layout.setContentsMargins(8, 4, 8, 4)
            self.banner_layout.setSpacing(8)
            
            self.banner_label = QLabel("Alt-Tab integration extension is not installed.")
            self.banner_layout.addWidget(self.banner_label, stretch=1)
            
            install_btn = QPushButton("Install Extension")
            install_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d08770;
                    color: #2e3440;
                    font-weight: bold;
                    font-size: 11px;
                    border-radius: 3px;
                    padding: 2px 6px;
                }
                QPushButton:hover {
                    background-color: #ebcb8b;
                }
            """)
            install_btn.clicked.connect(self._install_extension_from_banner)
            self.banner_layout.addWidget(install_btn)
            
            dismiss_btn = QPushButton("✕")
            dismiss_btn.setFixedSize(22, 22)
            dismiss_btn.setToolTip("Dismiss Banner")
            dismiss_btn.clicked.connect(self._dismiss_banner)
            self.banner_layout.addWidget(dismiss_btn)
            
            self.banner_widget = QWidget()
            self.banner_widget.setObjectName("BannerWidget")
            self.banner_widget.setLayout(self.banner_layout)
            self.banner_widget.setStyleSheet("""
                QWidget#BannerWidget {
                    background-color: #3b3322;
                    border: 1px solid #d08770;
                    border-radius: 4px;
                }
                QLabel {
                    color: #ebcb8b;
                    font-size: 11px;
                    font-weight: bold;
                    background: transparent;
                }
                QPushButton#DismissBtn {
                    background: transparent;
                    border: none;
                    color: #ebcb8b;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton#DismissBtn:hover {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 3px;
                }
            """)
            layout.addWidget(self.banner_widget)
        
        # Top buttons
        btn_layout = QHBoxLayout()
        btn_emerg = QPushButton("+ Sticky")
        btn_emerg.setToolTip("Create a persistent, always-on-top Sticky Note")
        btn_emerg.clicked.connect(lambda: self._note_manager.create_note("emergency"))
        
        btn_norm = QPushButton("+ Note")
        btn_norm.setToolTip("Create a standard Sticky Note")
        btn_norm.clicked.connect(lambda: self._note_manager.create_note("normal"))
        
        btn_defaults = QPushButton("⚙ Settings")
        btn_defaults.setToolTip("Configure default note styling, fonts, and dimensions")
        btn_defaults.clicked.connect(self._open_default_settings)

        btn_layout.addWidget(btn_emerg)
        btn_layout.addWidget(btn_norm)
        btn_layout.addWidget(btn_defaults)
        layout.addLayout(btn_layout)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget)
        
        # Bottom buttons
        bottom_btn_layout = QHBoxLayout()
        btn_show_all = QPushButton("Show All Notes")
        btn_show_all.clicked.connect(self._note_manager.show_all)
        
        btn_hide_all = QPushButton("Hide All Notes")
        btn_hide_all.clicked.connect(self._note_manager.hide_all)
        
        bottom_btn_layout.addWidget(btn_show_all)
        bottom_btn_layout.addWidget(btn_hide_all)
        layout.addLayout(bottom_btn_layout)
        
        # Connect signals
        self._note_manager.note_created.connect(self._on_note_created)
        self._note_manager.note_deleted.connect(self._on_note_deleted)
        self._note_manager.note_updated.connect(self._on_note_updated)
        
    def _dismiss_banner(self):
        if hasattr(self, 'banner_widget'):
            self.banner_widget.hide()
        self.settings.setValue("extension_banner_dismissed", True)

    def _install_extension_from_banner(self):
        extension_installer.install_and_enable_extension(self)
        if extension_installer.is_extension_installed():
            self._dismiss_banner()
        
    def _on_note_created(self, model):
        item = QListWidgetItem(self.list_widget)
        item.setData(Qt.ItemDataRole.UserRole, model.id)
        widget = NoteListItem(model, self._note_manager)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        
    def _on_note_deleted(self, note_id):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.list_widget.takeItem(i)
                break
                
    def _on_note_updated(self, model):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == model.id:
                widget = self.list_widget.itemWidget(item)
                if widget:
                    widget.update_model(model)
                break
                
    def _on_item_clicked(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        model = self._note_manager.get_note(note_id)
        if model:
            model.minimized = False
            self._note_manager.update_note(model)
        window = self._note_manager._windows.get(note_id)
        if not window and model:
            self._note_manager._create_window_for_model(model)
            window = self._note_manager._windows.get(note_id)
        if window:
            if hasattr(window, 'isMinimized') and window.isMinimized():
                window.showNormal()
            window.show()
            window.raise_()
            window.activateWindow()
            
    def _open_default_settings(self):
        from windows.default_settings_dialog import DefaultSettingsDialog
        dlg = DefaultSettingsDialog(self)
        dlg.exec()

    def closeEvent(self, event):
        from PyQt6.QtWidgets import QApplication
        self._note_manager.close_all_windows()
        event.accept()
        QApplication.instance().closeAllWindows()
        QApplication.instance().quit()
