__all__ = ['MainWindow', 'BookBrowserWidget']

import os

from PySide2.QtWidgets import QMainWindow

from src.config import Config
from src.ui.views.BookBrowserWidget import BookBrowserWidget

class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.setWindowTitle(Config.application_name)
        self.setFixedSize(900, 680)
        self.setCentralWidget(BookBrowserWidget(dirpath=os.path.join(Config.project_directory, "data"), parent=self))