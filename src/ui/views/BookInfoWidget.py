from copy import copy
from pprint import pformat

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QIcon, QPixmap
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget, QTextEdit
from PySide2 import QtWebEngineWidgets
from src.ui.views.icons import flag_label, image_url_label, image_label
import logging
logger = logging.getLogger('gui')
from config import AppState
config = AppState().config

class BookWidget(QWidget):
    def __init__(self, info, parent=None):
        super(BookWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.info = info
        cover_layout = QVBoxLayout()
        try:
            label = image_label(self.info.cover_image, 400)
        except AttributeError:
            label = image_url_label(self.info.image_url, 200)
        #label = image_label(None, 200)
        cover_layout.addWidget(label)
        cover_layout.addWidget(QLabel(self.info.title))
        self.layout().addLayout(cover_layout)
        self.layout().setAlignment(Qt.AlignTop)


class InfoWidget(QWidget):
    def __init__(self, info, parent=None):
        super(InfoWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.info = info
        try:
            self.add_widgets()
        except AttributeError as e:
            logger.warning('InfoWidget {}: {}'.format(self.info.title, e))

class WebInfoWidget(QWidget):
    def __init__(self, site: str, info, parent=None):
        super(WebInfoWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.site = site
        self.info = info
        self.webview = QWebEngineView()
        self.layout().addWidget(self.webview)
        try:
            self.url = self.info.__getattribute__(self.site).url
            self.webview.load(self.url)
        except AttributeError as e:
            logger.warning('WebInfoWidget {}: {}'.format(self.info.title, e))

    def reload(self):
        try:
            self.webview.load(self.url)
        except AttributeError:
            pass


class RawWidget(InfoWidget):
    def __init__(self, info, parent=None):
        super(RawWidget, self).__init__(info, parent)

        label = QLabel(str(self.info))
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout().addWidget(label)

    def add_widgets(self):
        pass

class BookInfoWidget(QWidget):
    def __init__(self, info, parent=None):
        super(BookInfoWidget, self).__init__(parent)

        self.info = info
        logging.getLogger('gui').info('select {}'.format(self.info.title))

        self.setLayout(QVBoxLayout())

        author = QLabel(self.info.title)
        author.setFont(QFont("Helvetica", pointSize=16, weight=75))
        author.setStyleSheet('color: blue')

        title = QLabel(self.info.author)
        title.setFont(QFont("Helvetica", pointSize=16, weight=75))
        title.setStyleSheet('color: gray')

        author_title = QHBoxLayout()
        author_title.addWidget(author)
        author_title.addWidget(title)
        self.layout().addLayout(author_title)

        lang_isbn = QHBoxLayout()
        lang_isbn.addWidget(flag_label(self.info.language, 25))
        lang_isbn.addWidget(QLabel(self.info.ISBN))

        self.layout().addLayout(lang_isbn)

        information_widget = QTabWidget()
        information_widget.addTab(BookWidget(self.info), 'book')
        information_widget.addTab(RawWidget(self.info), 'info')

        for site in ['openlibrary', 'goodreads', 'librarything']:
            try:
                self.info.__getattribute__(site).url
                information_widget.addTab(WebInfoWidget(site, self.info),
                                          QIcon(QPixmap('../resources/icons/{}.png'.format(site))),
                                        site.capitalize())
            except AttributeError:
                # no tab
                pass
        information_widget.setMovable(True)
        self.layout().addWidget(information_widget)
