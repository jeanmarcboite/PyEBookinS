import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QIcon, QPixmap
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget, QTextEdit

from config import AppState
from src.ui.views.icons import flag_label, image_url_label, image_label

logger = logging.getLogger('gui')

config = AppState().config


class BookWidget(QWidget):
    def __init__(self, info, parent=None):
        super(BookWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.info = info
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignLeft)

        cover_layout = QVBoxLayout()
        try:
            label = image_label(self.info.cover_image, 300)
        except AttributeError:
            try:
                label = image_url_label(self.info.image_url, 300)
            except AttributeError:
                label = image_label(None, 300)
        cover_layout.addWidget(label)
        cover_layout.addStretch()
        top_layout.addLayout(cover_layout)
        description_layout = QVBoxLayout()
        description_layout.setAlignment(Qt.AlignTop)
        description_label = QTextEdit(self.info.description)
        description_label.setMinimumSize(500, 300)
        description_label.setMaximumSize(700, 300)
        description_label.resize(700, 300)
        description_label.setReadOnly(True)
        description_layout.addWidget(description_label)
        top_layout.addLayout(description_layout)
        top_layout.addStretch()

        self.layout().addLayout(top_layout)


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
