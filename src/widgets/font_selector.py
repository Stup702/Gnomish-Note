from PyQt6.QtWidgets import QComboBox, QFontDialog
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import pyqtSignal

POPULAR_FONTS = [
    ("Sans Serif", "Sans Serif (Default)"),
    ("Cantarell", "Cantarell (GNOME)"),
    ("Noto Sans", "Noto Sans"),
    ("Ubuntu", "Ubuntu"),
    ("Roboto", "Roboto"),
    ("DejaVu Sans", "DejaVu Sans"),
    ("Liberation Sans", "Liberation Sans"),
    ("Monospace", "Monospace"),
    ("DejaVu Sans Mono", "DejaVu Sans Mono"),
    ("Serif", "Serif"),
    ("Comic Sans MS", "Comic Sans MS (Casual)"),
]

class CuratedFontComboBox(QComboBox):
    fontChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_family = "Sans Serif"
        self._populate()
        self.currentIndexChanged.connect(self._on_index_changed)

    def _populate(self):
        self.blockSignals(True)
        self.clear()
        installed = set(QFontDatabase.families())
        for family, display_name in POPULAR_FONTS:
            if family in ["Sans Serif", "Monospace", "Serif"] or family in installed:
                self.addItem(display_name, family)
        self.insertSeparator(self.count())
        self.addItem("Other System Font...", "__CUSTOM__")
        self.blockSignals(False)

    def current_family(self) -> str:
        return self._current_family

    def set_current_family(self, family: str):
        self._current_family = family
        self.blockSignals(True)
        for i in range(self.count()):
            if self.itemData(i) == family:
                self.setCurrentIndex(i)
                self.blockSignals(False)
                return
        # If not present in curated list, insert it cleanly
        idx = max(0, self.count() - 2)
        self.insertItem(idx, family, family)
        self.setCurrentIndex(idx)
        self.blockSignals(False)

    def _on_index_changed(self, index: int):
        data = self.itemData(index)
        if data == "__CUSTOM__":
            ok, font = QFontDialog.getFont(QFont(self._current_family), self.window(), "Select Font")
            if ok:
                self.set_current_family(font.family())
                self.fontChanged.emit(font.family())
            else:
                self.set_current_family(self._current_family)
        elif data:
            self._current_family = data
            self.fontChanged.emit(data)
