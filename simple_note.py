#!/usr/bin/env python3
import sys
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from PyQt6.QtGui import QColor, QPalette

class StickyNote(QWidget):
    def __init__(self):
        super().__init__()
        
        # --- THE SECRET SAUCE FOR FLOATING & NON-FOCUS-STEALING ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.ToolTip  # Tricks Wayland/GNOME into letting it float over everything
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        self.initUI()
        self.oldPos = self.pos()

    def initUI(self):
        self.setFixedSize(250, 250)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)

        # Background container for styling (rounded corners, color)
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: #fdf5c9; /* Sticky note yellow */
                border-radius: 8px;
                border: 1px solid #e1d599;
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(5, 5, 5, 5)

        # Top Bar (for dragging)
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(20)
        self.top_bar.setStyleSheet("background: transparent; border: none;")
        top_bar_layout = QHBoxLayout(self.top_bar)
        top_bar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Close Button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setStyleSheet("""
            QPushButton { 
                background: transparent; border: none; font-weight: bold; color: #888;
            }
            QPushButton:hover { color: #f00; }
        """)
        self.close_btn.clicked.connect(self.close)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(self.close_btn)

        # Text Area
        self.text_area = QTextEdit()
        self.text_area.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                font-family: 'Helvetica';
                font-size: 11pt;
                color: #333;
            }
        """)
        self.text_area.setPlaceholderText("Write your notes here...")

        container_layout.addWidget(self.top_bar)
        container_layout.addWidget(self.text_area)
        
        layout.addWidget(self.container)

    # --- DRAG & DROP LOGIC ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    # --- FOCUS LOGIC ---
    # Because ToolTip windows try to avoid focus, you need to explicitly 
    # activate it when the user clicks inside to allow them to type.
    def mouseReleaseEvent(self, event):
        self.activateWindow()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    note = StickyNote()
    
    # Use show() instead of showNormal() or similar to respect WA_ShowWithoutActivating
    note.show()
    
    sys.exit(app.exec())
