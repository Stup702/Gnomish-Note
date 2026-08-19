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
            self.type_label.setText("⚠")
            self.type_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
        else:
            self.type_label.setText("📌")
            self.type_label.setStyleSheet("color: #3498db; font-weight: bold; font-size: 14px;")
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
            self.type_label.setText("⚠")
            self.type_label.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
        else:
            self.type_label.setText("📌")
            self.type_label.setStyleSheet("color: #3498db; font-weight: bold; font-size: 14px;")
            
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
            self.banner_label = QLabel("Note: Custom extension required for proper Alt-Tab hiding.")
            self.banner_layout.addWidget(self.banner_label, stretch=1)
            
            dismiss_btn = QPushButton("✕")
            dismiss_btn.setFixedSize(24, 24)
            dismiss_btn.clicked.connect(self._dismiss_banner)
            self.banner_layout.addWidget(dismiss_btn)
            
            self.banner_widget = QWidget()
            self.banner_widget.setLayout(self.banner_layout)
            self.banner_widget.setStyleSheet("background-color: #fffae6; border: 1px solid #ffe58f;")
            layout.addWidget(self.banner_widget)
        
        # Top buttons
        btn_layout = QHBoxLayout()
        btn_emerg = QPushButton("+ Emergency")
        btn_emerg.clicked.connect(lambda: self._note_manager.create_note("emergency"))
        
        btn_norm = QPushButton("+ Note")
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
        self.banner_widget.hide()
        self.settings.setValue("extension_banner_dismissed", True)
        
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
