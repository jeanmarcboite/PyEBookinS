from copy import copy
from pprint import pformat

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget, QTextEdit

from src.ui.views.icons import flag_label


class InfoWidget(QWidget):
    def __init__(self, info, parent=None):
        super(InfoWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.info = info
        try:
            self.add_widgets()
        except AttributeError as e:
            print('{}: {}'.format(self.info.title, e))


class OpenLibraryWidget(InfoWidget):
    def __init__(self, info, parent=None):
        super(OpenLibraryWidget, self).__init__(info, parent)

    def add_widgets(self):
        if self.info.openlibrary:
            widget = QTextEdit(pformat(self.info.openlibrary, indent=4))
            widget.setReadOnly(True)
            self.layout().addWidget(widget)


class GoodreadsWidget(InfoWidget):
    def __init__(self, info, parent=None):
        super(GoodreadsWidget, self).__init__(info, parent)

    def add_widgets(self):
        if self.info.goodreads:
            author = QLabel(self.info.author)
            self.layout().addWidget(author)


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
        print('select {}'.format(self.info.title))

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
        information_widget.addTab(GoodreadsWidget(self.info), 'Goodreads')
        information_widget.addTab(OpenLibraryWidget(self.info), 'OpenLibrary')
        self.layout().addWidget(information_widget)
