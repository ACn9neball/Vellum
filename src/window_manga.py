import json_parsing
import zipfile
from pathlib import Path
from PyQt6.QtGui import QAction, QIcon, QKeyEvent, QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenuBar,
    QWidget,
    QStackedWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


class MainWindow(QMainWindow):
    go_back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manga Reader")
        self.resize(1000, 750)

        self.statusBar()

        self.default_settings = json_parsing.load_settings()

        self.current_scale_mode = 0
        self.page_number = 1
        self.total_pages = 0
        self.previousStep = 0
        self.file_paths = None
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

        self.left_image = QLabel()
        self.left_image.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        layout.addWidget(self.left_image)

        self.right_image = QLabel()
        self.right_image.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
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
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        self._build_file_menu(menu_bar)
        self._build_reader_menu(menu_bar)
        self._build_playback_menu(menu_bar)
        self._build_help_menu(menu_bar)

    def _build_file_menu(self, menu_bar: QMenuBar):
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction(QIcon(str(ASSETS_DIR / "document.png")), "&Open", self)
        open_action.setStatusTip("Open Manga")
        open_action.triggered.connect(self.openFile)
        file_menu.addAction(open_action)

        recent_action = QAction(
            QIcon(str(ASSETS_DIR / "documents.png")), "Open Recent", self
        )
        recent_action.setStatusTip("Open Recent Manga")
        file_menu.addAction(recent_action)

        collection_action = QAction(
            QIcon(str(ASSETS_DIR / "folder-open.png")), "Open Collection", self
        )
        collection_action.setStatusTip("Open Manga Collection")
        file_menu.addAction(collection_action)

        file_menu.addSeparator()

        close_action = QAction(QIcon(str(ASSETS_DIR / "cross.png")), "&Close", self)
        close_action.setStatusTip("Close File")
        file_menu.addAction(close_action)

        quit_action = QAction(
            QIcon(str(ASSETS_DIR / "door-open-out.png")), "&Quit", self
        )
        quit_action.setStatusTip("Quit Application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def _build_reader_menu(self, menu_bar: QMenuBar):
        reader_menu = menu_bar.addMenu("&Reader")
        fullscreen_action = QAction(
            QIcon(str(ASSETS_DIR / "application-resize-full.png")), "&Fullscreen", self
        )
        fullscreen_action.setStatusTip("Fullscreen Mode")
        reader_menu.addAction(fullscreen_action)
        readmode_action = QAction(
            QIcon(str(ASSETS_DIR / "e-book-reader.png")), "Read Mode", self
        )
        readmode_action.setStatusTip("Change Reading Mode")
        reader_menu.addAction(readmode_action)
        backcolor_action = QAction(
            QIcon(str(ASSETS_DIR / "border-color.png")), "Background Color", self
        )
        backcolor_action.setStatusTip("Change Background Color")
        reader_menu.addAction(backcolor_action)
        scalemode_action = QAction(
            QIcon(str(ASSETS_DIR / "edit-scale.png")), "Scale Mode", self
        )
        scalemode_action.setStatusTip("Change Image Scalling")
        reader_menu.addAction(scalemode_action)

    def _build_playback_menu(self, menu_bar: QMenuBar):
        reader_menu = menu_bar.addMenu("&Playback")
        playlist_action = QAction(
            QIcon(str(ASSETS_DIR / "folder-open-document-music-playlist.png")),
            "&Playlist",
            self,
        )
        reader_menu.addAction(playlist_action)
        previous_action = QAction(
            QIcon(str(ASSETS_DIR / "document-page-previous.png")), "&Previous", self
        )
        previous_action.triggered.connect(self.previousPage)
        reader_menu.addAction(previous_action)
        next_action = QAction(
            QIcon(str(ASSETS_DIR / "document-page-next.png")), "&Next", self
        )
        next_action.triggered.connect(self.nextPage)
        reader_menu.addAction(next_action)

    def _build_help_menu(self, menu_bar: QMenuBar):
        help_menu = menu_bar.addMenu("&Help")
        help_action = QAction(QIcon(str(ASSETS_DIR / "question.png")), "Help", self)
        help_menu.addAction(help_action)
        about_action = QAction(
            QIcon(str(ASSETS_DIR / "information.png")), "About", self
        )
        help_menu.addAction(about_action)

    def display(self, path):
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

            if self.double:
                self.view_stack.setCurrentIndex(0)

                with cbz.open(pages[self.page_number - 1]) as f:
                    self.left_pixmap = QPixmap()
                    self.left_pixmap.loadFromData(f.read())

                if self.page_number < self.total_pages:
                    with cbz.open(pages[self.page_number]) as f:
                        self.right_pixmap = QPixmap()
                        self.right_pixmap.loadFromData(f.read())
                else:
                    self.right_pixmap = None
            else:
                self.view_stack.setCurrentIndex(1)

                with cbz.open(pages[self.page_number - 1]) as f:
                    self.left_pixmap = QPixmap()
                    self.left_pixmap.loadFromData(f.read())
                self.right_pixmap = None

            self.imageScale(0)

            loaded_msg = (
                f"Loaded side-by-side spread"
                if self.right_pixmap
                else f"Loaded single page: {pages[self.page_number - 1]}"
            )
            self.statusBar().showMessage(loaded_msg, 3000)

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
                label.setScaledContents(True)
                label.setPixmap(pixmap)
            case 2 | 3:
                label.setScaledContents(False)
                label.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
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
            case _:
                super().keyPressEvent(event)

    def nextPage(self):
        step = 2 if self.double else 1
        if self.page_number + step <= self.total_pages:
            self.page_number += step
            self.display(self.file_paths[self.file_count])
            self.previousStep = step

    def previousPage(self):
        if self.page_number - self.previousStep >= 1:
            self.page_number -= self.previousStep
            self.display(self.file_paths[self.file_count])

    def openFile(self):
        self.page_number = 1
        self.total_pages = 0
        self.file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select File",
            self.default_settings["folder_path"],
            "Comic Book Zip (*.cbz)",
        )
        self.display(self.file_path)

    def receive_data(self, data):
        self.file_paths = data
        self.page_number = 1
        self.file_count = 0
        self.display(data[self.file_count])
