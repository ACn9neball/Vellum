from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel


class ClickableLabel(QLabel):
    doubleClick = pyqtSignal()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.doubleClick.emit()
            event.accept()
