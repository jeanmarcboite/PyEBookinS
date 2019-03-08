import logging
import os
from pathlib import Path

from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtWidgets import QScrollArea, \
    QSplitter, QFrame, QVBoxLayout, QPushButton
from xdg import BaseDirectory

from config import AppState
from src.bookinfo.calibredb import CalibreDB
from src.bookinfo.ebook import BookInfo
from src.ui.views.BookTreeView import BookTreeView, BookItem, AuthorItem
from src.ui.views.InfoWidget import InfoWidget

config = AppState().config


# noinspection PyPep8Naming
class BookBrowserWidget(QSplitter):
    logger = logging.getLogger('gui')

    def __init__(self, parent=None):
        super(BookBrowserWidget, self).__init__(Qt.Horizontal, parent)

        self.files = []
        books = config['books']
        for b in books:
            book = b.as_str()
            if os.path.isfile(book):
                self.files.append(book)
            elif os.path.isdir(book):
                self.files.extend(BookBrowserWidget.find_files(book.as_str))
            else:
                data_dir = BaseDirectory.save_data_path('{}/{}'.format(config['application_name'],
                                                                       book))
                if os.path.isdir(data_dir):
                    self.files.extend(BookBrowserWidget.find_files(data_dir))
                else:
                    BookBrowserWidget.logger.warning("book '%s' not found")

        BookBrowserWidget.logger.info("Import %d files", len(self.files))

        self.calibre_db = self.add_calibre_db()

        self.book_tree_view = self.add_book_tree_view()
        self.populate()

        self.info_widget = self.add_info_widget()

    @staticmethod
    def add_calibre_db():
        try:
            calibre = config['calibre'].as_str()
            if not os.path.exists(calibre):
                calibre = BaseDirectory.save_data_path('{}/{}'.format(config['application_name'],
                                                                      calibre))
            if os.path.isdir(calibre):
                calibre = os.path.join(calibre, 'metadata.db')

            if os.path.isfile(calibre):
                return CalibreDB(database='sqlite:///' + calibre)
        except AttributeError:
            return None
        return None

    def add_book_tree_view(self):
        frame = QFrame()
        frame.setLayout(QVBoxLayout())
        button = QPushButton('fill items')
        button.clicked.connect(self.populate)
        frame.layout().addWidget(button)

        book_tree_view = BookTreeView()
        book_tree_view.clicked[QModelIndex].connect(self.item_selected)
        frame.layout().addWidget(book_tree_view)
        self.addWidget(frame)

        return book_tree_view

    def add_info_widget(self):
        info_widget = InfoWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.resize(800, 600)
        self.addWidget(scroll_area)

        return info_widget

    def populate(self):
        for file in self.files:
            self.add_item(file)

    def item_selected(self, index):
        item = index.model().itemFromIndex(index)
        # need TODO something for AuthorItem
        if type(item) is AuthorItem:
            self.info_widget.set_author_info(item.wikipedia)
        if type(item) is BookItem:
            self.info_widget.set_book_info(item.info)

    def add_item(self, file):
        info = BookInfo(file)

        if self.calibre_db:
            try:
                info.calibre = self.calibre_db[info.ISBN]
            except (KeyError, AttributeError) as kae:
                BookBrowserWidget.logger.debug(kae)
        self.book_tree_view.add_item(info)

    @staticmethod
    def find_files(dirpath, extensions=AppState().config['ebook_extensions'].get()):
        files = []
        for extension in extensions:
            files.extend(Path(dirpath).glob('**/*.' + extension))
        return files
