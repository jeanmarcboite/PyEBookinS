import confuse
from PySide2.QtWidgets import QMainWindow, QLabel, QPushButton

from config import AppState
from .AppMenu import add_menu
from .BookBrowserWidget import BookBrowserWidget
from .SettingsDialog import SettingsDialog

config = AppState().config


class MainWindow(QMainWindow):
    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.setWindowTitle(config['application_name'].as_str())
        self.resize(config['window']['width'].as_number(), config['window']['height'].as_number())

        try:
            add_menu(self.menuBar())

            self.browser = BookBrowserWidget(parent=self)
            self.setCentralWidget(self.browser)

            self.button = QPushButton('settings')
            self.statusBar().addWidget(self.button)
            self.statusBar().addWidget(QLabel('status...........................'))
            self.button.clicked.connect(self.settings_dialog)
        except confuse.NotFoundError as e:
            self.setCentralWidget(QLabel('Configuration error: {}'.format(e)))

    def settings_dialog(self):
        print(SettingsDialog.dialog(self))
