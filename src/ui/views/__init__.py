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
        self.setFixedSize(900, 680)
        dirpath = config['database'].as_filename()
        if not os.path.exists(dirpath):
            dirpath = BaseDirectory.save_data_path('{}/{}'.format(config['application_name'],
                                                                  config['database']))
        try:
            self.setCentralWidget(BookBrowserWidget(dirpath=dirpath,
                                                    parent=self))
        except confuse.NotFoundError as e:
            print(e)
            self.setCentralWidget(QLabel('Configuration error: {}'.format(e)))
