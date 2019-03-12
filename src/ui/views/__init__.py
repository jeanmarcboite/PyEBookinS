import confuse
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QStatusBar, QPushButton, QAction
from PySide2.QtCore import Slot
from config import AppState
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
            self.file_menu()
            self.view_menu()

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

    def action(self, pixmap, text, toolTip, shortcut, func):
        icon = QIcon(QPixmap(pixmap))
        this = QAction(icon, text, self)
        this.setToolTip(toolTip)
        this.setShortcut(shortcut)
        this.triggered.connect(func)

        return this

    def file_menu(self):
            fileMenu = self.menuBar().addMenu('File')
            fileMenu.addAction(self.action(pixmap='../resources/icons/Open-folder-add-icon.png',
                                text='Add', toolTip='add data',
                               shortcut='Ctrl+A', func=self.add_directory))
            fileMenu.addAction(self.action('../resources/icons/Actions-application-exit-icon.png',
                                           'Exit', 'Close program', 'Ctrl+Q', self.close))

            return fileMenu

    def view_menu(self):
            viewMenu = self.menuBar().addMenu('View')
            hiddenButton = QAction('Hidden', self)
            hiddenButton.setCheckable(True)
            hiddenButton.triggered.connect(self.display_hidden)
            viewMenu.addAction(hiddenButton)

            otherButton = QAction('Other', self)
            otherButton.triggered.connect(self.display_hidden)
            viewMenu.addAction(otherButton)

            viewView = viewMenu.addMenu('view')
            otherButton = QAction('Other view', self)
            otherButton.setWhatsThis('What?')
            otherButton.triggered.connect(lambda action='yy', arg='xx': self.action_function(action,arg))
            viewView.addAction(otherButton)

            return viewMenu

    @Slot(str, str)
    def display_hidden(self, action, arg):
        print(arg)
        print(action)
        print(type(action))

    def action_function(self, action, arg):
        print(action)
        print(type(action))
        print(arg)

    def add_directory(self):
        print('add')