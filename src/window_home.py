import json
from pathlib import Path
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QComboBox,
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
APP_NAME = "vellum"
APP_AUTHOR = "Personal"


class MainWindow(QMainWindow):
    data_submitted = pyqtSignal(str)

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

        iconOpen = QIcon(str(ASSETS_DIR / "document.png"))
        btnOpen = QPushButton()
        btnOpen.setIcon(iconOpen)
        btnOpen.clicked.connect(self.openFile)
        btnOpen.setToolTip("Open File")

        iconMultiple = QIcon(str(ASSETS_DIR / "documents.png"))
        btnMultiple = QPushButton()
        btnMultiple.setIcon(iconMultiple)
        btnMultiple.clicked.connect(self.settings_toggled)
        btnMultiple.setToolTip("Open Files")

        iconFolder = QIcon(str(ASSETS_DIR / "folder-open.png"))
        btnFolder = QPushButton()
        btnFolder.setIcon(iconFolder)
        btnFolder.clicked.connect(self.settings_toggled)
        btnFolder.setToolTip("Open Folder")

        space_container = QWidget()
        space_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        iconSetting = QIcon(str(ASSETS_DIR / "gear.png"))
        btnSetting = QPushButton()
        btnSetting.setIcon(iconSetting)
        btnSetting.setCheckable(True)
        btnSetting.clicked.connect(self.settings_toggled)
        btnSetting.setToolTip("Global Settings")

        iconExit = QIcon(str(ASSETS_DIR / "door-open-out.png"))
        btnExit = QPushButton()
        btnExit.setIcon(iconExit)
        btnExit.clicked.connect(self.close)
        btnExit.setToolTip("Exit App")

        left_layout.addWidget(btnOpen)
        left_layout.addWidget(btnMultiple)
        left_layout.addWidget(btnFolder)
        left_layout.addWidget(space_container)
        left_layout.addWidget(btnSetting)
        left_layout.addWidget(btnExit)
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
        else:
            while self.right_layout.count():
                item = self.right_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

    def settings(self):
        theme_container = QWidget()
        theme_layout = QHBoxLayout(theme_container)

        lblTheme = QLabel("Theme:")
        self.cbxPath = QComboBox()
        self.cbxPath.addItems(["Default", "Light", "Dark"])
        self.cbxPath.setCurrentText(self.default_settings["theme"])
        self.cbxPath.currentTextChanged.connect(self.themeSwitcher)

        theme_layout.addWidget(lblTheme, stretch=2)
        theme_layout.addWidget(self.cbxPath, stretch=8)

        path_container = QWidget()
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

        background_container = QWidget()
        background_layout = QHBoxLayout(background_container)

        lblBackground = QLabel("Default Background Color:")
        self.cbxBackground = QComboBox()
        self.cbxBackground.addItems(["Automatic", "Black", "Grey", "White"])
        self.cbxBackground.setCurrentText(self.default_settings["background_color"])
        self.cbxBackground.currentTextChanged.connect(self.backgroundColorSwitcher)

        background_layout.addWidget(lblBackground, stretch=2)
        background_layout.addWidget(self.cbxBackground, stretch=8)

        reading_container = QWidget()
        reading_layout = QHBoxLayout(reading_container)

        lblReading = QLabel("Default Reading Mode:")
        self.cbxReading = QComboBox()
        self.cbxReading.addItems(["LTR", "RTL", "Vertical", "Vertical-Continuous"])
        self.cbxReading.setCurrentText(self.default_settings["reading_mode"])
        self.cbxReading.currentTextChanged.connect(self.readerModeSwitcher)

        reading_layout.addWidget(lblReading, stretch=2)
        reading_layout.addWidget(self.cbxReading, stretch=8)

        space_container = QWidget()
        space_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.right_layout.addWidget(theme_container)
        self.right_layout.addWidget(path_container)
        self.right_layout.addWidget(background_container)
        self.right_layout.addWidget(reading_container)
        self.right_layout.addWidget(space_container)

    def pathDefault(self):
        folderPath = QFileDialog.getExistingDirectory(
            None, "Select File", self.default_settings["folder_path"]
        )
        self.default_settings["folder_path"] = folderPath
        self.save_settings(self.default_settings)
        self.ledPath.setText(self.default_settings["folder_path"])

    def themeSwitcher(self, theme):
        self.default_settings["theme"] = theme
        self.save_settings(self.default_settings)

    def backgroundColorSwitcher(self, color):
        self.default_settings["background_color"] = color
        self.save_settings(self.default_settings)

    def readerModeSwitcher(self, type):
        self.default_settings["reading_mode"] = type
        self.save_settings(self.default_settings)

    def load_settings(self):
        default_settings = {
            "theme": "Light",
            "folder_path": "/home/",
            "background_color": "Automatic",
            "reading_mode": "LTR",
        }
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

    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            self.default_settings["folder_path"],
            "Comic Book Zip (*.cbz)",
        )
        self.data_submitted.emit(file_path)
