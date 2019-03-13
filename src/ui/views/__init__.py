import confuse
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QStatusBar, QPushButton, QAction
from PySide2.QtCore import Slot
from config import AppState
from .AppMenu import add_menu
from .SettingsDialog import SettingsDialog
from .BookBrowserWidget import BookBrowserWidget

config = AppState().config

class Action(QAction):
    def __init__(self, **kwargs):
        super(Action, self).__init__(**kwargs)

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