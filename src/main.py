import sys
from PyQt6.QtWidgets import QApplication
import window_home
import window_manga


class AppController:
    def __init__(self):
        self.window_home = window_home.MainWindow()
        self.window_manga = window_manga.MainWindow()

        self.window_home.data_submitted.connect(self.switch_to_window_two)
        self.window_manga.go_back_requested.connect(self.switch_to_window_one)

    def start(self):
        self.window_home.show()

    def switch_to_window_two(self, data):
        self.window_manga.receive_data(data)
        self.window_manga.show()
        self.window_home.close()

    def switch_to_window_one(self):
        self.window_home.show()
        self.window_manga.close()


app = QApplication(sys.argv)
controller = AppController()
controller.start()
sys.exit(app.exec())
