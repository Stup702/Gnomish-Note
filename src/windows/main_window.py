from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel,
    QLineEdit, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QSettings, QSize
from PyQt6.QtGui import QTextDocumentFragment
from core import extension_installer

class NoteListItem(QWidget):
    def __init__(self, model, note_manager):
        super().__init__()
        self._model = model
        self._note_manager = note_manager
        self.setObjectName("NoteCard")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 8, 8)
        main_layout.setSpacing(10)
        
        # Color pip & type indicator
        self.type_label = QLabel()
        self._update_badge()
        main_layout.addWidget(self.type_label)
        
        # Text details (Title + Preview)
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)
        
        self.title_label = QLabel()
        self.title_label.setObjectName("CardTitle")
        self.title_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        
        self.preview_label = QLabel()
        self.preview_label.setObjectName("CardPreview")
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.preview_label)
        main_layout.addLayout(text_layout, stretch=1)
        
        self._update_text()
        
        # Actions button cluster (Toggle Type, Rename, Delete)
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.toggle_type_btn = QPushButton()
        self.toggle_type_btn.setObjectName("CardActionBtn")
        self.toggle_type_btn.setFixedSize(26, 26)
        self.toggle_type_btn.clicked.connect(self._on_toggle_type)
        actions_layout.addWidget(self.toggle_type_btn)
        
        self._update_badge()

        # Rename button
        rename_btn = QPushButton("✏")
        rename_btn.setObjectName("CardActionBtn")
        rename_btn.setToolTip("Rename Note")
        rename_btn.setFixedSize(26, 26)
        rename_btn.clicked.connect(self._on_rename)
        actions_layout.addWidget(rename_btn)

        # Delete button
        del_btn = QPushButton("🗑")
        del_btn.setObjectName("CardActionBtn")
        del_btn.setToolTip("Delete Note")
        del_btn.setFixedSize(26, 26)
        del_btn.clicked.connect(self._on_delete)
        actions_layout.addWidget(del_btn)

        main_layout.addLayout(actions_layout)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QWidget#NoteCard {
                background-color: #262626;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
            QWidget#NoteCard:hover {
                background-color: #2f2f2f;
                border: 1px solid rgba(255, 255, 255, 0.16);
            }
            QLabel#CardTitle {
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
                background: transparent;
            }
            QLabel#CardPreview {
                color: #9a9996;
                font-size: 11px;
                background: transparent;
            }
            QPushButton#CardActionBtn {
                background: transparent;
                border: none;
                border-radius: 13px;
                color: #888888;
                font-size: 13px;
                font-family: "Noto Color Emoji", "DejaVu Sans", "Segoe UI Emoji", sans-serif;
            }
            QPushButton#CardActionBtn:hover {
                background: rgba(255, 255, 255, 0.15);
                color: #ffffff;
            }
        """)

    def _update_badge(self):
        if self._model.note_type == "emergency":
            self.type_label.setText("●")
            self.type_label.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 14px; background: transparent;")
            self.type_label.setToolTip("Always-on-top Sticky Note")
            if hasattr(self, 'toggle_type_btn'):
                self.toggle_type_btn.setText("🗖")
                self.toggle_type_btn.setToolTip("Convert to Standard Note")
        else:
            self.type_label.setText("●")
            self.type_label.setStyleSheet("color: #2ec27e; font-weight: bold; font-size: 14px; background: transparent;")
            self.type_label.setToolTip("Standard Note")
            if hasattr(self, 'toggle_type_btn'):
                self.toggle_type_btn.setText("📌")
                self.toggle_type_btn.setToolTip("Convert to Always-on-Top Sticky Note")

    def _on_toggle_type(self):
        updated = self._note_manager.toggle_note_type(self._model.id)
        if updated:
            self.update_model(updated)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._open_note()
        super().mousePressEvent(event)

    def _open_note(self):
        window = self._note_manager._windows.get(self._model.id)
        if not window:
            self._note_manager._create_window_for_model(self._model)
        self._note_manager.bring_to_front(self._model.id)

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
        preview = clean_text[:40].replace('\n', ' ') if clean_text else "Empty note"
        
        if title:
            self.title_label.setText(title)
            self.title_label.show()
            self.preview_label.setText(preview)
        else:
            self.title_label.hide()
            self.preview_label.setText(preview)
            self.preview_label.setStyleSheet("color: #e0e0e0; font-size: 12px; font-weight: 500;")

    def update_model(self, model):
        self._model = model
        self._update_badge()
        self._update_text()

    def matches_query(self, query: str) -> bool:
        if not query:
            return True
        q = query.lower()
        title = getattr(self._model, "title", "").lower()
        content = getattr(self._model, "content_html", "")
        clean_text = QTextDocumentFragment.fromHtml(content).toPlainText().lower()
        return q in title or q in clean_text

    def sizeHint(self):
        return QSize(0, 54)


class MainWindow(QMainWindow):
    def __init__(self, note_manager):
        super().__init__()
        self._note_manager = note_manager
        
        self.setWindowTitle("Gnomish Note")
        self.resize(460, 540)
        self.setMinimumSize(400, 420)
        
        import os
        from PyQt6.QtGui import QIcon
        from core.paths import get_app_icon_path
        icon_path = get_app_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Extension Banner — only show if extension is not installed
        self.settings = QSettings("gnome-sticky-notes", "main")
        if (not extension_installer.is_extension_installed() and
                not self.settings.value("extension_banner_dismissed", False, type=bool)):
            self.banner_layout = QHBoxLayout()
            self.banner_layout.setContentsMargins(10, 6, 10, 6)
            self.banner_layout.setSpacing(8)
            
            self.banner_label = QLabel("Alt-Tab integration extension not installed.")
            self.banner_layout.addWidget(self.banner_label, stretch=1)
            
            install_btn = QPushButton("Install")
            install_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d08770;
                    color: #1e1e1e;
                    font-weight: bold;
                    font-size: 11px;
                    border-radius: 4px;
                    padding: 3px 8px;
                }
                QPushButton:hover {
                    background-color: #ebcb8b;
                }
            """)
            install_btn.clicked.connect(self._install_extension_from_banner)
            self.banner_layout.addWidget(install_btn)
            
            dismiss_btn = QPushButton("✕")
            dismiss_btn.setObjectName("DismissBtn")
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
                    border-radius: 6px;
                }
                QLabel {
                    color: #ebcb8b;
                    font-size: 11px;
                    font-weight: 600;
                    background: transparent;
                }
                QPushButton#DismissBtn {
                    background: transparent;
                    border: none;
                    color: #ebcb8b;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton#DismissBtn:hover {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 3px;
                }
            """)
            layout.addWidget(self.banner_widget)
        
        # Header Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        btn_emerg = QPushButton("+ Sticky")
        btn_emerg.setObjectName("BtnSticky")
        btn_emerg.setToolTip("Create a persistent, always-on-top Sticky Note")
        btn_emerg.clicked.connect(lambda: self._note_manager.create_note("emergency"))
        
        btn_norm = QPushButton("+ Note")
        btn_norm.setObjectName("BtnNote")
        btn_norm.setToolTip("Create a standard Sticky Note")
        btn_norm.clicked.connect(lambda: self._note_manager.create_note("normal"))
        
        btn_defaults = QPushButton("⚙ Settings")
        btn_defaults.setObjectName("BtnSettings")
        btn_defaults.setToolTip("Configure default note styling, fonts, and dimensions")
        btn_defaults.clicked.connect(self._open_default_settings)

        btn_layout.addWidget(btn_emerg, stretch=1)
        btn_layout.addWidget(btn_norm, stretch=1)
        btn_layout.addWidget(btn_defaults)
        layout.addLayout(btn_layout)
        
        # Search Filter Bar
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchInput")
        self.search_input.setPlaceholderText("🔍 Search notes...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_input)

        # Note Cards List
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("NoteList")
        self.list_widget.setSpacing(6)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.list_widget, stretch=1)
        
        # Empty State Label
        self.empty_label = QLabel("No notes yet.\nClick + Sticky or + Note above to create one.")
        self.empty_label.setObjectName("EmptyLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

        # Bottom Bar (Note Count & Show/Hide Controls)
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(2, 2, 2, 2)

        self.count_label = QLabel("0 notes")
        self.count_label.setObjectName("CountLabel")
        bottom_bar.addWidget(self.count_label)
        
        bottom_bar.addStretch()

        btn_show_all = QPushButton("Show All")
        btn_show_all.setObjectName("BtnPill")
        btn_show_all.clicked.connect(self._note_manager.show_all)
        
        btn_hide_all = QPushButton("Hide All")
        btn_hide_all.setObjectName("BtnPill")
        btn_hide_all.clicked.connect(self._note_manager.hide_all)
        
        bottom_bar.addWidget(btn_show_all)
        bottom_bar.addWidget(btn_hide_all)
        layout.addLayout(bottom_bar)
        
        # Apply Global Styling
        self._apply_theme()

        # Connect NoteManager signals
        self._note_manager.note_created.connect(self._on_note_created)
        self._note_manager.note_deleted.connect(self._on_note_deleted)
        self._note_manager.note_updated.connect(self._on_note_updated)
        
    def _apply_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget#CentralWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton#BtnSticky {
                background-color: #3b2c1a;
                color: #e67e22;
                border: 1px solid #d08770;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                padding: 7px 12px;
            }
            QPushButton#BtnSticky:hover {
                background-color: #4a3821;
                border: 1px solid #ebcb8b;
            }
            QPushButton#BtnNote {
                background-color: #1a3324;
                color: #2ec27e;
                border: 1px solid #27ae60;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                padding: 7px 12px;
            }
            QPushButton#BtnNote:hover {
                background-color: #244733;
                border: 1px solid #2ecc71;
            }
            QPushButton#BtnSettings {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                font-size: 12px;
                padding: 7px 10px;
            }
            QPushButton#BtnSettings:hover {
                background-color: #383838;
                color: #ffffff;
            }
            QLineEdit#SearchInput {
                background-color: #282828;
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 12px;
            }
            QLineEdit#SearchInput:focus {
                border: 1px solid #3584e4;
                background-color: #2c2c2c;
            }
            QListWidget#NoteList {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget#NoteList::item {
                background: transparent;
                border: none;
                padding: 0px;
            }
            QLabel#EmptyLabel {
                color: #777777;
                font-size: 12px;
                padding: 30px;
            }
            QLabel#CountLabel {
                color: #777777;
                font-size: 11px;
            }
            QPushButton#BtnPill {
                background-color: #282828;
                color: #b0b0b0;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 5px;
                font-size: 11px;
                padding: 4px 8px;
            }
            QPushButton#BtnPill:hover {
                background-color: #363636;
                color: #ffffff;
            }
        """)

    def _dismiss_banner(self):
        if hasattr(self, 'banner_widget'):
            self.banner_widget.hide()
        self.settings.setValue("extension_banner_dismissed", True)

    def _install_extension_from_banner(self):
        extension_installer.install_and_enable_extension(self)
        if extension_installer.is_extension_installed():
            self._dismiss_banner()
        
    def _on_note_created(self, model):
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, model.id)
        widget = NoteListItem(model, self._note_manager)
        item.setSizeHint(widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, widget)
        self._update_list_state()
        
    def _on_note_deleted(self, note_id):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == note_id:
                self.list_widget.takeItem(i)
                break
        self._update_list_state()
                
    def _on_note_updated(self, model):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == model.id:
                widget = self.list_widget.itemWidget(item)
                if widget:
                    widget.update_model(model)
                    item.setSizeHint(widget.sizeHint())
                break
        self._update_list_state()

    def _on_search_changed(self, text: str):
        query = text.strip()
        visible_count = 0
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            if widget:
                matches = widget.matches_query(query)
                item.setHidden(not matches)
                if matches:
                    visible_count += 1
        self._update_list_state()

    def _update_list_state(self):
        total = self.list_widget.count()
        query = self.search_input.text().strip()
        
        visible = sum(1 for i in range(total) if not self.list_widget.item(i).isHidden())
        
        if query:
            self.count_label.setText(f"{visible} of {total} notes")
        else:
            self.count_label.setText(f"{total} note{'s' if total != 1 else ''}")

        if total == 0:
            self.empty_label.setText("No notes yet.\nClick + Sticky or + Note above to create one.")
            self.empty_label.show()
            self.list_widget.hide()
        elif visible == 0 and query:
            self.empty_label.setText(f"No notes matching \"{query}\".")
            self.empty_label.show()
            self.list_widget.hide()
        else:
            self.empty_label.hide()
            self.list_widget.show()
                
    def _on_item_clicked(self, item):
        note_id = item.data(Qt.ItemDataRole.UserRole)
        model = self._note_manager.get_note(note_id)
        if model:
            window = self._note_manager._windows.get(note_id)
            if not window:
                self._note_manager._create_window_for_model(model)
            self._note_manager.bring_to_front(note_id)
            
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
