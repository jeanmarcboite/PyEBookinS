from copy import copy
from pprint import pformat

from PySide2.QtGui import QFont, QIcon, QPixmap
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget, QTextEdit
from PySide2 import QtWebEngineWidgets
from src.ui.views.icons import flag_label
import logging
logger = logging.getLogger('gui')
from config import AppState
config = AppState().config

class InfoWidget(QWidget):
    def __init__(self, info, parent=None):
        super(InfoWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.info = info
        try:
            self.add_widgets()
        except AttributeError as e:
            logger.error('{}: {}'.format(self.info.title, e))

class WebInfoWidget(InfoWidget):
    def __init__(self, info, parent=None):
        super(WebInfoWidget, self).__init__(info, parent)

    def load(self, url):
        self.url = url
        self.webview = QWebEngineView()
        self.webview.load(self.url)
        self.layout().addWidget(self.webview)

    def reload(self):
        self.webview.load(self.url)


class OpenLibraryWidget(WebInfoWidget):
    def __init__(self, info, parent=None):
        super(OpenLibraryWidget, self).__init__(info, parent)

    def add_widgets(self):
        if self.info.openlibrary:
            self.load(config['openlibrary']['url'].as_str().format(self.info.openlibrary['key']))


class GoodreadsWidget(WebInfoWidget):
    def __init__(self, info, parent=None):
        super(GoodreadsWidget, self).__init__(info, parent)

    def add_widgets(self):
        if self.info.goodreads:
            self.load(self.info.goodreads['book']['link'])

class LibrarythingWidget(WebInfoWidget):
    def __init__(self, info, parent=None):
        super(LibrarythingWidget, self).__init__(info, parent)

    def add_widgets(self):
        if self.info.librarything:
            self.load(self.info.librarything['url'])


class RawWidget(InfoWidget):
    def __init__(self, info, parent=None):
        super(RawWidget, self).__init__(info, parent)

    def add_widgets(self):
        info = copy(self.info)
        del info.cover_image
        self.layout().addWidget(QLabel(str(info)))


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
        information_widget.addTab(RawWidget(self.info), 'info')
        information_widget.addTab(OpenLibraryWidget(self.info),
                                  QIcon(QPixmap('../resources/icons/OpenLibrary_400x400.jpg')),
                                  'OpenLibrary')
        information_widget.addTab(GoodreadsWidget(self.info), QIcon(QPixmap('../resources/icons/iconfinder_goodreads_43148.png')), 'Goodreads')
        information_widget.addTab(LibrarythingWidget(self.info),
                                  QIcon(QPixmap('../resources/icons/LibraryThing_icon.jpg')), 'LibraryThing')
        information_widget.setMovable(True)
        self.layout().addWidget(information_widget)
