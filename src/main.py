import sys
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vellum")
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        left_container = QWidget()
        right_container = QWidget()
        left_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        right_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        left_layout = QVBoxLayout(left_container)

        iconSetting = QIcon(str(ASSETS_DIR / "gear.png"))
        btnSetting = QPushButton()
        btnSetting.setIcon(iconSetting)
        btnSetting.setCheckable(True)
        btnSetting.clicked.connect(self.settings_toggled)

        left_layout.addWidget(btnSetting)
        layout.addWidget(left_container, stretch=1)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)

        layout.addWidget(divider)

        self.right_layout = QVBoxLayout(right_container)
        layout.addWidget(right_container, stretch=10)

        self.setCentralWidget(container)

    def settings_toggled(self, clicked):
        if clicked:
            self.settings()

    def settings(self):
        path_container = QWidget()
        path_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        path_layout = QHBoxLayout(path_container)

        lblPath = QLabel("Default Manga Path")
        ledPath = QLineEdit()
        iconFolder = QIcon(str(ASSETS_DIR / "folder-open.png"))
        btnPath = QPushButton()
        btnPath.setIcon(iconFolder)

        path_layout.addWidget(lblPath, stretch=2)
        path_layout.addWidget(ledPath, stretch=5)
        path_layout.addWidget(btnPath, stretch=1)

        self.right_layout.addWidget(path_container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
