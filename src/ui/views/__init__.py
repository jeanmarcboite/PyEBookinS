import confuse
from PySide2.QtCore import QSettings, QCoreApplication, QSize, QPoint
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
        QCoreApplication.setOrganizationName('Box')
        QCoreApplication.setOrganizationDomain('box.com')
        QCoreApplication.setApplicationName('BookinS')
        self.setWindowGeometry()
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

    def moveEvent(self, event):
        rc = super(MainWindow, self).moveEvent(event)
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        settings.setValue('pos', self.pos())
        settings.endGroup()
        return rc

    def resizeEvent(self, event):
        rc = super(MainWindow, self).resizeEvent(event)
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        settings.setValue('size', self.size())
        settings.endGroup()
        return rc

    def setWindowGeometry(self):
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        self.resize(settings.value(
            'size',
            QSize(config[self.__class__.__name__]['width'].as_number(),
                  config[self.__class__.__name__]['height'].as_number())))
        self.move(settings.value(
            'pos',
            QPoint(config[self.__class__.__name__]['x'].as_number(),
                  config[self.__class__.__name__]['y'].as_number())))
        settings.endGroup()
