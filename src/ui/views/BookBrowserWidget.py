import logging
import os
from pathlib import Path

from PySide2.QtCore import Qt, QModelIndex
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QScrollArea, \
    QSplitter, QFrame, QVBoxLayout, QPushButton
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from xdg import BaseDirectory

from config import AppState
from src.bookinfo.calibredb import CalibreDB
from src.bookinfo.ebook import BookInfo
from src.ui.views.BookTreeView import BookTreeView, BookItem
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

        self.calibre_db = None
        try:
            calibre = config['calibre'].as_str()
            if not os.path.exists(calibre):
                calibre = BaseDirectory.save_data_path('{}/{}'.format(config['application_name'],
                                                                      calibre))
            if os.path.isdir(calibre):
                calibre = os.path.join(calibre, 'metadata.db')

            if os.path.isfile(calibre):
                self.calibre_db = CalibreDB(database='sqlite:///' + calibre)
        except AttributeError:
            pass

        self.addWidget(self.left_frame())
        self.populate()

        self.info_widget = InfoWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.resize(800, 600)
        self.addWidget(scroll_area)

    def left_frame(self):
        frame = QFrame()
        frame.setLayout(QVBoxLayout())
        button = QPushButton('fill items')
        button.clicked.connect(self.populate)
        frame.layout().addWidget(button)

        self.book_tree_view = BookTreeView()
        self.book_tree_view.clicked[QModelIndex].connect(self.item_selected)
        frame.layout().addWidget(self.book_tree_view)

        return frame

    def populate(self):
        for file in self.files:
            self.add_item(self.book_tree_view, file)

    def item_selected(self, index):
        item = self.book_tree_view.model().itemFromIndex(index)
        # need TODO something for AuthorItem
        if type(item) is BookItem:
            self.info_widget.set_info(item.info)

    def selectionChanged(self, new, old):
        self.info_widget.set_info(self.tree_widget.currentItem().info)

    def add_item(self, widget, file):
        info = BookInfo(file)

        if self.calibre_db:
            try:
                info.calibre = self.calibre_db[info.ISBN]
            except (KeyError, AttributeError):
                pass

        widget.add_item(info)

    @staticmethod
    def find_files(dirpath, extensions=AppState().config['ebook_extensions'].get()):
        files = []
        for extension in extensions:
            files.extend(Path(dirpath).glob('**/*.' + extension))
        return files

    @staticmethod
    def files_by(files, key, calibre_db=None):
        by = dict()
        for file in files:
            info = BookInfo(file)

            if calibre_db:
                try:
                    info.calibre = calibre_db[info.ISBN]
                except (KeyError, AttributeError):
                    pass

            try:
                attr = getattr(info, key)
                if attr not in by.keys():
                    by[attr] = []
                by[attr].append(info)
            except AttributeError:
                pass
        return by
