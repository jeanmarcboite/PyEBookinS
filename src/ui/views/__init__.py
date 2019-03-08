import confuse
from PySide2.QtWidgets import QMainWindow, QLabel

from config import AppState
from .BookBrowserWidget import BookBrowserWidget

config = AppState().config


class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.setWindowTitle(config['application_name'].as_str())
        self.resize(config['window']['width'].as_number(), config['window']['height'].as_number())

        try:
            self.browser = BookBrowserWidget(parent=self)
            self.setCentralWidget(self.browser)

        except confuse.NotFoundError as e:
            self.setCentralWidget(QLabel('Configuration error: {}'.format(e)))
