import os, sys
from pathlib import Path
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
import json_parsing

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


class MainWindow(QMainWindow):
    data_submitted = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vellum")
        container = QWidget()

        self.default_settings = json_parsing.load_settings()
        self.default_recents = json_parsing.load_recents()

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
        btnMultiple.clicked.connect(self.openFiles)
        btnMultiple.setToolTip("Open Files")

        iconRecent = QIcon(str(ASSETS_DIR / "documents-stack.png"))
        self.btnRecent = QPushButton()
        self.btnRecent.setIcon(iconRecent)
        self.btnRecent.setCheckable(True)
        self.btnRecent.clicked.connect(self.recents_toggled)
        self.btnRecent.setToolTip("Open Recent Files")

        iconFolder = QIcon(str(ASSETS_DIR / "folder-open.png"))
        btnFolder = QPushButton()
        btnFolder.setIcon(iconFolder)
        btnFolder.clicked.connect(self.openFolder)
        btnFolder.setToolTip("Open Folder")

        space_container = QWidget()
        space_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        iconSetting = QIcon(str(ASSETS_DIR / "gear.png"))
        self.btnSetting = QPushButton()
        self.btnSetting.setIcon(iconSetting)
        self.btnSetting.setCheckable(True)
        self.btnSetting.clicked.connect(self.settings_toggled)
        self.btnSetting.setToolTip("Global Settings")

        iconExit = QIcon(str(ASSETS_DIR / "door-open-out.png"))
        btnExit = QPushButton()
        btnExit.setIcon(iconExit)
        btnExit.clicked.connect(self.close)
        btnExit.setToolTip("Exit App")

        left_layout.addWidget(btnOpen)
        left_layout.addWidget(btnMultiple)
        left_layout.addWidget(btnFolder)
        left_layout.addWidget(self.btnRecent)
        left_layout.addWidget(space_container)
        left_layout.addWidget(self.btnSetting)
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
            self.clearRight()
            self.settings()
            self.btnRecent.setChecked(False)
        else:
            self.clearRight()

    def recents_toggled(self, clicked):
        if clicked:
            self.clearRight()
            self.recents()
            self.btnSetting.setChecked(False)
        else:
            self.clearRight()

    def clearRight(self):
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def settings(self):
        lblGroupOne = QLabel("General")
        dividerOne = QFrame()
        dividerOne.setFrameShape(QFrame.Shape.HLine)
        dividerOne.setFrameShadow(QFrame.Shadow.Sunken)

        lblGroupTwo = QLabel("Display and Interface")
        dividerTwo = QFrame()
        dividerTwo.setFrameShape(QFrame.Shape.HLine)
        dividerTwo.setFrameShadow(QFrame.Shadow.Sunken)

        lblGroupThree = QLabel("Layout and Reading Direction")
        dividerThree = QFrame()
        dividerThree.setFrameShape(QFrame.Shape.HLine)
        dividerThree.setFrameShadow(QFrame.Shadow.Sunken)

        # Theme Row
        theme_container = QWidget()
        theme_layout = QHBoxLayout(theme_container)
        lblTheme = QLabel("Theme:")
        self.cbxTheme = QComboBox()
        self.cbxTheme.addItems(["Default", "Light", "Dark"])
        self.cbxTheme.setCurrentText(self.default_settings["theme"])
        self.cbxTheme.currentTextChanged.connect(self.themeSwitcher)
        theme_layout.addWidget(lblTheme, stretch=2)
        theme_layout.addWidget(self.cbxTheme, stretch=8)

        # Default Path Row
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

        # Background Row
        background_container = QWidget()
        background_layout = QHBoxLayout(background_container)
        lblBackground = QLabel("Default Background Color:")
        self.cbxBackground = QComboBox()
        self.cbxBackground.addItems(["Automatic", "Black", "Grey", "White"])
        self.cbxBackground.setCurrentText(self.default_settings["background_color"])
        self.cbxBackground.currentTextChanged.connect(self.backgroundColorSwitcher)
        background_layout.addWidget(lblBackground, stretch=2)
        background_layout.addWidget(self.cbxBackground, stretch=8)

        # Reading Mode Row
        reading_container = QWidget()
        reading_layout = QHBoxLayout(reading_container)
        lblReading = QLabel("Default Reading Mode:")
        self.cbxReading = QComboBox()
        self.cbxReading.addItems(
            [
                "LTR",
                "RTL",
                "Vertical",
                "Vertical Continuous",
            ]
        )
        self.cbxReading.setCurrentText(self.default_settings["reading_mode"])
        self.cbxReading.currentTextChanged.connect(self.readerModeSwitcher)
        reading_layout.addWidget(lblReading, stretch=2)
        reading_layout.addWidget(self.cbxReading, stretch=8)

        # Fullscreen Row
        fullscreen_container = QWidget()
        fullscreen_layout = QHBoxLayout(fullscreen_container)
        lblFullscreen = QLabel("Fullscreen:")
        self.chxFullscreen = QCheckBox()
        self.chxFullscreen.setChecked(self.default_settings["fullscreen"])
        self.chxFullscreen.stateChanged.connect(self.fullscreenSwitcher)
        fullscreen_layout.addWidget(lblFullscreen)
        fullscreen_layout.addStretch()
        fullscreen_layout.addWidget(self.chxFullscreen)

        # Page Layout Row
        page_container = QWidget()
        page_layout = QHBoxLayout(page_container)
        lblPage = QLabel("Page Layout:")
        self.cbxPage = QComboBox()
        self.cbxPage.addItems(["Single Page", "Double Page", "Automatic"])
        self.cbxPage.setCurrentText(self.default_settings["page_layout"])
        self.cbxPage.currentTextChanged.connect(self.pageLayoutSwitcher)
        page_layout.addWidget(lblPage, stretch=2)
        page_layout.addWidget(self.cbxPage, stretch=8)

        # Animation Row
        animation_container = QWidget()
        animation_layout = QHBoxLayout(animation_container)
        lblAnimation = QLabel("Animation:")
        self.chxAnimation = QCheckBox()
        self.chxAnimation.setChecked(self.default_settings["animation"])
        self.chxAnimation.stateChanged.connect(self.animationSwitcher)
        animation_layout.addWidget(lblAnimation)
        animation_layout.addStretch()
        animation_layout.addWidget(self.chxAnimation)

        # Scale Type Row
        scale_container = QWidget()
        scale_layout = QHBoxLayout(scale_container)
        lblScale = QLabel("Scale Type:")
        self.cbxScale = QComboBox()
        self.cbxScale.addItems(
            ["Fit Screen", "Fit Width", "Fit Height", "Stretch", "Automatic"]
        )
        self.cbxScale.setCurrentText(self.default_settings["scale_type"])
        self.cbxScale.currentTextChanged.connect(self.scaleTypeSwitcher)
        scale_layout.addWidget(lblScale, stretch=2)
        scale_layout.addWidget(self.cbxScale, stretch=8)

        # Swapped Page Row
        swapped_container = QWidget()
        swapped_layout = QHBoxLayout(swapped_container)
        lblSwapped = QLabel("Swapped Double Pages:")
        self.chxSwapped = QCheckBox()
        self.chxSwapped.setChecked(self.default_settings["swapped_page"])
        self.chxSwapped.stateChanged.connect(self.swappedPageSwitcher)
        swapped_layout.addWidget(lblSwapped)
        swapped_layout.addStretch()
        swapped_layout.addWidget(self.chxSwapped)

        btnClear = QPushButton("Clear")
        btnClear.clicked.connect(self.clearSettingToggled)

        space_container = QWidget()
        space_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        self.right_layout.addWidget(lblGroupOne)
        self.right_layout.addWidget(dividerOne)
        self.right_layout.addWidget(theme_container)
        self.right_layout.addWidget(path_container)
        self.right_layout.addWidget(lblGroupTwo)
        self.right_layout.addWidget(dividerTwo)
        self.right_layout.addWidget(fullscreen_container)
        self.right_layout.addWidget(animation_container)
        self.right_layout.addWidget(background_container)
        self.right_layout.addWidget(lblGroupThree)
        self.right_layout.addWidget(dividerThree)
        self.right_layout.addWidget(reading_container)
        self.right_layout.addWidget(page_container)
        self.right_layout.addWidget(scale_container)
        self.right_layout.addWidget(swapped_container)
        self.right_layout.addWidget(btnClear)
        self.right_layout.addWidget(space_container)

    def recents(self):
        lblRecent = QLabel("Recent Files")
        dividerOne = QFrame()
        dividerOne.setFrameShape(QFrame.Shape.HLine)
        dividerOne.setFrameShadow(QFrame.Shadow.Sunken)

        self.lwdRecents = QListWidget()
        recents = self.default_recents["recent_files"]
        recents.reverse()
        self.lwdRecents.addItems(recents)
        self.lwdRecents.itemDoubleClicked.connect(self.recentItemClicked)

        btnClear = QPushButton("Clear")
        btnClear.clicked.connect(self.clearRecentToggled)

        self.right_layout.addWidget(lblRecent)
        self.right_layout.addWidget(dividerOne)
        self.right_layout.addWidget(self.lwdRecents)
        self.right_layout.addWidget(btnClear)

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

    def fullscreenSwitcher(self, f):
        isfullscreen = True if f == 2 else False
        self.default_settings["fullscreen"] = isfullscreen
        self.save_settings(self.default_settings)

    def pageLayoutSwitcher(self, type):
        self.default_settings["page_layout"] = type
        self.save_settings(self.default_settings)

    def animationSwitcher(self, a):
        animation = True if a == 2 else False
        self.default_settings["animation"] = animation
        self.save_settings(self.default_settings)

    def scaleTypeSwitcher(self, type):
        self.default_settings["scale_type"] = type
        self.save_settings(self.default_settings)

    def swappedPageSwitcher(self, s):
        swapped = True if s == 2 else False
        self.default_settings["swapped_page"] = swapped
        self.save_settings(self.default_settings)

    def recentItemClicked(self, item):
        file_path = item.text()
        file_paths = [file_path]
        if file_path != "":
            self.default_recents = json_parsing.save_recent(
                self.default_recents, file_paths[0]
            )
            self.data_submitted.emit(file_paths)

    def clearRecentToggled(self):
        mbxConfirm = QMessageBox()
        mbxConfirm.setWindowTitle("Clear All")
        mbxConfirm.setText("Clear All Recent Entries")
        mbxConfirm.setIcon(QMessageBox.Icon.Warning)
        mbxConfirm.setStandardButtons(
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes
        )
        mbxConfirm.setDefaultButton(QMessageBox.StandardButton.No)

        response = mbxConfirm.exec()
        if response == QMessageBox.StandardButton.Yes:
            json_parsing.reset_recents()
            self.lwdRecents.clear()

    def clearSettingToggled(self):
        mbxConfirm = QMessageBox()
        mbxConfirm.setWindowTitle("Revert to default settings")
        mbxConfirm.setText("Go back to default settings")
        mbxConfirm.setIcon(QMessageBox.Icon.Warning)
        mbxConfirm.setStandardButtons(
            QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes
        )
        mbxConfirm.setDefaultButton(QMessageBox.StandardButton.No)

        response = mbxConfirm.exec()
        if response == QMessageBox.StandardButton.Yes:
            json_parsing.reset_settings()
            mbxReboot = QMessageBox()
            mbxReboot.setWindowTitle("Reboot application")
            mbxReboot.setText("To revert settings reboot is needed. Reboot?")
            mbxReboot.setIcon(QMessageBox.Icon.Question)
            mbxReboot.setStandardButtons(
                QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes
            )
            mbxReboot.setDefaultButton(QMessageBox.StandardButton.No)

            response2 = mbxReboot.exec()
            if response2 == QMessageBox.StandardButton.Yes:
                os.execv(sys.executable, [sys.executable] + sys.argv)

    def openFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            self.default_settings["folder_path"],
            "Comic Book Zip (*.cbz)",
        )
        file_paths = [file_path]
        if file_path != "":
            self.default_recents = json_parsing.save_recent(
                self.default_recents, file_paths[0]
            )
            self.data_submitted.emit(file_paths)

    def openFiles(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            None,
            "Select File",
            self.default_settings["folder_path"],
            "Comic Book Zip (*.cbz)",
        )

        if file_paths != []:

            self.default_recents = json_parsing.save_recent(
                self.default_recents, file_paths[0]
            )
            self.data_submitted.emit(file_paths)

    def openFolder(self):
        folder_path = QFileDialog.getExistingDirectory(
            None,
            "Select File",
            self.default_settings["folder_path"],
        )

        if not folder_path:
            return

        folder_path = Path(folder_path)
        file_paths = [str(file) for file in folder_path.glob("*.cbz")]
        if file_paths != []:
            self.default_recents = json_parsing.save_recent(
                self.default_recents, file_paths[0]
            )
            self.data_submitted.emit(file_paths)

    def save_settings(self, data):
        json_parsing.save_settings(data)
        self.default_settings = json_parsing.load_settings()
