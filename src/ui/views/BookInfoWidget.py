from PySide2.QtGui import QFont, QPixmap
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTabWidget

from src.ui.views.icons import flag_label

class OpenLibraryWidget(QWidget):
    def __init__(self, info, parent=None):
        super(OpenLibraryWidget, self).__init__(parent)

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
        information_widget.addTab(OpenLibraryWidget(self.info), 'OpenLibrary')
        self.layout().addWidget(information_widget)


