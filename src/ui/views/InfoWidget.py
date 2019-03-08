from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel

from src.ui.views.BookInfoWidget import BookInfoWidget

class AuthorInfoWidget(QWidget):
    def __init__(self, url: str, parent=None):
        super(AuthorInfoWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.webview = QWebEngineView()
        self.layout().addWidget(self.webview)
        self.webview.load(url)

class InfoWidget(QWidget):
    def __init__(self, parent=None):
        super(InfoWidget, self).__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel('no selection'))
        self.info = None

    def clean(self):
        while True:
            child = self.layout().takeAt(0)
            if child:
                child.widget().deleteLater()
            else:
                break

    def set_widget(self, widget):
        self.clean()
        self.layout().addWidget(widget)

    def set_book_info(self, info):
        self.info = info
        self.set_widget(BookInfoWidget(info))

    def set_author_info(self, url):
        self.url = url
        self.set_widget(AuthorInfoWidget(url))
