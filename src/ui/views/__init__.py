__all__ = ['MainWindow', 'BookBrowserWidget']

import os
import confuse
from config import AppState
from xdg import BaseDirectory

from PySide2.QtWidgets import QMainWindow, QLabel

config = AppState().config
from src.ui.views.BookBrowserWidget import BookBrowserWidget


class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.setWindowTitle(config['application_name'].as_str())
        self.resize(config['window']['width'].as_number(), config['window']['height'].as_number())

        try:
            self.setCentralWidget(BookBrowserWidget(parent=self))
        except confuse.NotFoundError as e:
            self.setCentralWidget(QLabel('Configuration error: {}'.format(e)))
