import json_parsing, zipfile
from pathlib import Path
from PyQt6.QtGui import QAction, QActionGroup, QIcon, QKeyEvent, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
)
from widgets import ClickableLabel

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


class MainWindow(QMainWindow):
    go_back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.statusBar()
        self.default_settings = json_parsing.load_settings()
        self.default_recents = json_parsing.load_recents()

        self.localFullscreen = self.default_settings["fullscreen"]
        backgroundColor = self.default_settings["background_color"]
        self.background(backgroundColor)

        self.current_scale_mode = 0
        self.page_number = 1
        self.total_pages = 0
        self.previousStep = 0
        self.file_paths = []
        self.file_count = 0
        self.double = True

        self.left_pixmap = None
        self.right_pixmap = None

        self._init_menu_bar()

        self.view_stack = QStackedWidget()
        self.setCentralWidget(self.view_stack)

        self._init_double_widget()
        self._init_single_widget()

    def _init_double_widget(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.left_image = ClickableLabel()
        self.left_image.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.left_image.doubleClick.connect(
            lambda: self.fullscreen(not self.localFullscreen)
        )
        layout.addWidget(self.left_image)

        self.right_image = ClickableLabel()
        self.right_image.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.right_image.doubleClick.connect(
            lambda: self.fullscreen(not self.localFullscreen)
        )
        layout.addWidget(self.right_image)

        self.view_stack.addWidget(container)

    def _init_single_widget(self):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.center_image = QLabel()
        self.center_image.setAlignment(
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self.center_image)

        self.view_stack.addWidget(container)

    def _init_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        self._build_file_menu(self.menu_bar)
        self._build_reader_menu(self.menu_bar)
        self._build_playback_menu(self.menu_bar)
        self._build_help_menu(self.menu_bar)

    def _build_file_menu(self, menu_bar: QMenuBar):
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction(QIcon(str(ASSETS_DIR / "document.png")), "&Open", self)
        open_action.setStatusTip("Open Manga")
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)

        multiple_action = QAction(
            QIcon(str(ASSETS_DIR / "documents.png")), "&Open Multiple", self
        )
        multiple_action.setStatusTip("Open Multiple Files")
        multiple_action.triggered.connect(self.openFiles)
        file_menu.addAction(multiple_action)

        collection_action = QAction(
            QIcon(str(ASSETS_DIR / "folder-open.png")), "Open Collection", self
        )
        collection_action.setStatusTip("Open Manga Collection")
        collection_action.triggered.connect(self.openFolder)
        file_menu.addAction(collection_action)

        file_submenu = file_menu.addMenu("Open Recent Manga")
        recents = self.default_recents["recent_files"]

        for recent in recents:
            action = QAction(recent, self)
            action.triggered.connect(lambda _, path=recent: self.open(path))
            file_submenu.addAction(action)

        file_menu.addSeparator()

        close_action = QAction(QIcon(str(ASSETS_DIR / "cross.png")), "&Close", self)
        close_action.setStatusTip("Close File")
        close_action.triggered.connect(self.go_back_requested.emit)
        file_menu.addAction(close_action)

        quit_action = QAction(
            QIcon(str(ASSETS_DIR / "door-open-out.png")), "&Quit", self
        )
        quit_action.setStatusTip("Quit Application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def _build_reader_menu(self, menu_bar: QMenuBar):
        reader_menu = menu_bar.addMenu("&Reader")
        self.fullscreen_action = QAction("&Fullscreen", self)
        self.fullscreen_action.setStatusTip("Fullscreen Mode")
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.setChecked(self.localFullscreen)
        self.fullscreen_action.triggered.connect(
            lambda _, c=self.localFullscreen: self.fullscreen(c)
        )
        reader_menu.addAction(self.fullscreen_action)

        readmode_submenu = reader_menu.addMenu("Reading Mode")
        mode = self.default_settings["reading_mode"]
        modes = ["LTR", "RTL", "Vertical", "Vertical Continuous"]
        mode_group = QActionGroup(self)

        for m in modes:
            action = QAction(m, self)
            action.setCheckable(True)
            # action.triggered.connect(lambda _, path=m: self.open(path))
            mode_group.addAction(action)
            readmode_submenu.addAction(action)

        if mode_group.actions():
            for i, m in enumerate(modes):
                if m == mode:
                    mode_group.actions()[i].setChecked(True)

        background_submenu = reader_menu.addMenu("Background Color")
        color = self.default_settings["background_color"]
        colors = ["Automatic", "Black", "White", "Grey"]
        color_group = QActionGroup(self)

        for c in colors:
            action = QAction(c, self)
            action.setCheckable(True)
            action.triggered.connect(lambda: self.background(c))
            color_group.addAction(action)
            background_submenu.addAction(action)

        if color_group.actions():
            for i, c in enumerate(colors):
                if c == color:
                    color_group.actions()[i].setChecked(True)

        scalemode_submenu = reader_menu.addMenu("Scale Mode")
        scale = self.default_settings["scale_type"]
        scales = ["Fit Screen", "Fit Width", "Fit Height", "Stretch", "Automatic"]
        scale_group = QActionGroup(self)

        for s in scales:
            action = QAction(s, self)
            action.setCheckable(True)
            # action.triggered.connect(lambda: self.background(c))
            scale_group.addAction(action)
            scalemode_submenu.addAction(action)

        if scale_group.actions():
            for i, s in enumerate(scales):
                if s == scale:
                    scale_group.actions()[i].setChecked(True)

        layout_submenu = reader_menu.addMenu("Page Layout")
        layout = self.default_settings["page_layout"]
        layouts = ["Single Page", "Double Page", "Automatic"]
        layout_group = QActionGroup(self)

        for l in layouts:
            action = QAction(l, self)
            action.setCheckable(True)
            # action.triggered.connect(lambda: self.background(c))
            layout_group.addAction(action)
            layout_submenu.addAction(action)

        if layout_group.actions():
            for i, l in enumerate(layouts):
                if l == layout:
                    layout_group.actions()[i].setChecked(True)

    def _build_playback_menu(self, menu_bar: QMenuBar):
        playback_menu = menu_bar.addMenu("&Playback")

        playlist_submenu = playback_menu.addMenu("Open Recent Manga")
        playlist = self.file_paths

        for p in playlist:
            action = QAction(p, self)
            action.triggered.connect(lambda _, path=p: self.open(path))
            playlist_submenu.addAction(action)
        previous_action = QAction(
            QIcon(str(ASSETS_DIR / "book-open-previous.png")), "&Previous", self
        )
        previous_action.triggered.connect(self.previousPage)
        playback_menu.addAction(previous_action)
        next_action = QAction(
            QIcon(str(ASSETS_DIR / "book-open-next.png")), "&Next", self
        )
        next_action.triggered.connect(self.nextPage)
        playback_menu.addAction(next_action)

        pChapter_action = QAction(
            QIcon(str(ASSETS_DIR / "document-page-previous.png")),
            "&Previous Chapter",
            self,
        )
        pChapter_action.triggered.connect(self.previousChapter)
        playback_menu.addAction(pChapter_action)
        nChapter_action = QAction(
            QIcon(str(ASSETS_DIR / "document-page-next.png")), "&Next Chapter", self
        )
        nChapter_action.triggered.connect(self.nextChapter)
        playback_menu.addAction(nChapter_action)

    def _build_help_menu(self, menu_bar: QMenuBar):
        help_menu = menu_bar.addMenu("&Help")
        help_action = QAction(QIcon(str(ASSETS_DIR / "question.png")), "Help", self)
        help_menu.addAction(help_action)
        about_action = QAction(
            QIcon(str(ASSETS_DIR / "information.png")), "About", self
        )
        help_menu.addAction(about_action)

    def display(self, path):
        fullScreen = self.default_settings["fullscreen"]
        self.fullscreen(fullScreen)
        if not path or not Path(path).exists():
            return

        with zipfile.ZipFile(path, "r") as cbz:
            files = sorted(cbz.namelist())
            pages = [
                f
                for f in files
                if f.lower().endswith((".png", ".jpeg", ".jpg", ".webp"))
            ]

            if not pages:
                self.statusBar().showMessage(
                    "No valid image files found inside CBZ.", 3000
                )
                return

            self.total_pages = len(pages)

            with cbz.open(pages[self.page_number - 1]) as f:
                pix_map = QPixmap()
                pix_map.loadFromData(f.read())
                self.detect_page_type(pix_map.width(), pix_map.height())

            match self.default_settings["reading_mode"]:
                case "LTR" | "RTL":
                    if self.double:
                        if self.default_settings["swapped_page"]:
                            self.view_stack.setCurrentIndex(0)
                            self.right_pixmap = self.load_pixmap(
                                cbz, pages, self.page_number - 1
                            )
                            self.left_pixmap = self.load_pixmap(
                                cbz, pages, self.page_number
                            )
                        else:
                            self.view_stack.setCurrentIndex(0)
                            self.left_pixmap = self.load_pixmap(
                                cbz, pages, self.page_number - 1
                            )
                            self.right_pixmap = self.load_pixmap(
                                cbz, pages, self.page_number
                            )
                    else:
                        self.view_stack.setCurrentIndex(1)
                        self.left_pixmap = self.load_pixmap(
                            cbz, pages, self.page_number - 1
                        )
                        self.right_pixmap = None

                    self.view_stack.adjustSize()
                    self.imageScale(0)
                case "Vertical":
                    self.double = False
                    self.view_stack.setCurrentIndex(1)
                    self.left_pixmap = self.load_pixmap(
                        cbz, pages, self.page_number - 1
                    )
                    self.right_pixmap = None
                    self.view_stack.adjustSize()
                    self.imageScale(3)
                case "Vertical Continuous":
                    pass

            loaded_msg = (
                f"Loaded side-by-side spread"
                if self.right_pixmap
                else f"Loaded single page: {pages[self.page_number - 1]}"
            )
            self.statusBar().showMessage(loaded_msg, 3000)

    def load_pixmap(self, cbz, pages, index) -> QPixmap | None:
        if 0 <= index < len(pages):
            with cbz.open(pages[index]) as f:
                pixmap = QPixmap()
                pixmap.loadFromData(f.read())
                return pixmap
        return None

    def imageScale(self, count):
        self.current_scale_mode = count

        if self.double:
            if self.left_pixmap and not self.left_pixmap.isNull():
                self._render_page(self.left_image, self.left_pixmap, count)
            else:
                self.left_image.clear()

            if self.right_pixmap and not self.right_pixmap.isNull():
                self._render_page(self.right_image, self.right_pixmap, count)
            else:
                self.right_image.clear()
        else:
            if self.left_pixmap and not self.left_pixmap.isNull():
                self._render_page(self.center_image, self.left_pixmap, count)
            else:
                self.center_image.clear()

    def _render_page(self, label: QLabel, pixmap: QPixmap, mode: int):
        match mode:
            case 0:
                label.setScaledContents(False)
                target_size = self.centralWidget().size()
                if self.double:
                    target_size.setWidth(int(target_size.width() / 2))

                scaled = pixmap.scaled(
                    target_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                label.setPixmap(scaled)
            case 1:
                label.setScaledContents(False)
                target_height = self.centralWidget().height()

                scaled = pixmap.scaledToHeight(
                    target_height, Qt.TransformationMode.SmoothTransformation
                )
                label.setPixmap(scaled)
            case 2:
                label.setScaledContents(False)
                target_width = self.centralWidget().width()

                scaled = pixmap.scaledToWidth(
                    target_width, Qt.TransformationMode.SmoothTransformation
                )
                label.setPixmap(scaled)
            case 3:
                label.setScaledContents(True)
                label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.file_paths and self.file_count < len(self.file_paths):
            if self.file_paths[self.file_count]:
                self.imageScale(self.current_scale_mode)

    def detect_page_type(self, width, height):
        aspect_ratio = width / height
        if aspect_ratio >= 1.1:
            self.double = False
        else:
            self.double = True

    def keyPressEvent(self, event: QKeyEvent):
        match event.key():
            case Qt.Key.Key_Right:
                self.nextPage()
            case Qt.Key.Key_N:
                self.nextPage()
            case Qt.Key.Key_Left:
                self.previousPage()
            case Qt.Key.Key_P:
                self.previousPage()
            case Qt.Key.Key_Escape:
                if self.localFullscreen:
                    self.localFullscreen = False
                    self.fullscreen(False)
            case _:
                super().keyPressEvent(event)

    def nextPage(self):
        step = 2 if self.double else 1
        if self.page_number + step <= self.total_pages:
            self.page_number += step
            self.display(self.file_paths[self.file_count])
            self.previousStep = step
        elif self.page_number + step > self.total_pages:
            self.nextChapter()

    def previousPage(self):
        if self.page_number - self.previousStep >= 1:
            self.page_number -= self.previousStep
            self.display(self.file_paths[self.file_count])
        elif self.page_number - self.previousStep < 1:
            self.previousChapter()

    def nextChapter(self):
        data = self.file_paths
        if self.file_count < len(data) - 1:
            self.file_count += 1
            self.page_number = 1
            self.previousStep = 0
            self.file_path = data[self.file_count]
            self.default_recents = json_parsing.save_recent(
                self.default_recents, data[self.file_count]
            )
            self.display(data[self.file_count])

    def previousChapter(self):
        data = self.file_paths
        if self.file_count > 0:
            self.file_count -= 1
            self.page_number = 1
            self.previousStep = 0
            self.file_path = data[self.file_count]
            self.default_recents = json_parsing.save_recent(
                self.default_recents, data[self.file_count]
            )
            self.display(data[self.file_count])

    def open(self, file_path):
        self.file_path = file_path
        self.file_paths = [self.file_path]
        if self.file_path != "":
            self.default_recents = json_parsing.save_recent(
                self.default_recents, self.file_paths[0]
            )
            self.display(self.file_path)

    def openFile(self):
        self.page_number = 1
        self.total_pages = 0
        self.file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            self.default_settings["folder_path"],
            "Comic Book Zip (*.cbz)",
        )
        file_paths = [self.file_path]
        if self.file_path != "":
            self.default_recents = json_parsing.save_recent(
                self.default_recents, file_paths[0]
            )
            self.display(self.file_path)

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
            self.file_path = file_paths[0]
            self.display(self.file_path)

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
            self.file_path = file_paths[0]
            self.display(self.file_path)

    def fullscreen(self, f: bool):
        if f:
            self.menu_bar.hide()
            self.showFullScreen()
            self.localFullscreen = True
        else:
            self.menu_bar.show()
            self.showNormal()
            self.localFullscreen = False

        self.fullscreen_action.setChecked(self.localFullscreen)

    def background(self, backgroundColor):
        theme = self.default_settings["theme"]
        match backgroundColor:
            case "Automatic":
                match theme:
                    case "Default":
                        self.setStyleSheet("QMainWindow { background-color: grey; }")
                    case "Light":
                        self.setStyleSheet("QMainWindow { background-color: white; }")
                    case "Dark":
                        self.setStyleSheet("QMainWindow { background-color: black; }")
            case "Black":
                self.setStyleSheet("QMainWindow { background-color: black; }")
            case "Grey":
                self.setStyleSheet("QMainWindow { background-color: grey; }")
            case "White":
                self.setStyleSheet("QMainWindow { background-color: white; }")

        self.style().unpolish(self)
        self.style().polish(self)

    def receive_data(self, data):
        self.file_paths = data
        self.page_number = 1
        self.file_count = 0
        self.display(data[self.file_count])
