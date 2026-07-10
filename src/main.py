import sys
import json
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
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
from platformdirs import user_config_dir

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"
APP_NAME = "Vellum"
APP_AUTHOR = "Personal"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vellum")
        container = QWidget()

        self.config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
        self.settings_file = self.config_dir / "settings.json"
        self.default_settings = self.load_settings()

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

        lblPath = QLabel("Default Manga Path:")
        self.ledPath = QLineEdit()
        self.ledPath.setText(self.default_settings["folder_path"])
        iconFolder = QIcon(str(ASSETS_DIR / "folder-open.png"))
        btnPath = QPushButton()
        btnPath.setIcon(iconFolder)
        btnPath.clicked.connect(self.pathDefault)

        path_layout.addWidget(lblPath, stretch=2)
        path_layout.addWidget(self.ledPath, stretch=7)
        path_layout.addWidget(btnPath, stretch=1)

        self.right_layout.addWidget(path_container)

    def pathDefault(self):
        folderPath = QFileDialog.getExistingDirectory(
            None, "Select File", self.default_settings["folder_path"]
        )
        default_settings = {"theme": "light", "folder_path": folderPath}
        self.save_settings(default_settings)
        self.ledPath.setText(self.default_settings["folder_path"])

    def load_settings(self):
        default_settings = {"theme": "light", "folder_path": "/home/"}
        if not self.settings_file.exists():
            self.save_settings(default_settings)
            return default_settings

        with open(self.settings_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_settings(self, data):
        self.config_dir.mkdir(parents=True, exist_ok=True)

        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.default_settings = self.load_settings()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
