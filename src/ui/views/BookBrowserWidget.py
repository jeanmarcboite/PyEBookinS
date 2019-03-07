import os
from pathlib import Path
import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QScrollArea, \
    QSplitter
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
from xdg import BaseDirectory

from config import AppState
from src.bookinfo.calibredb import CalibreDB
from src.bookinfo.ebook import book_info, BookInfo
from src.ui.views.BookTreeWidget import BookTreeWidget
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

        default_pixmap = QPixmap("../resources/icons/iconfinder_book_285636.png")
        #self.tree_widget = BookBrowserWidget.FileTreeWidget(BookBrowserWidget.files_by(files, 'author', calibre_db),
        #                                                    default_pixmap)

        self.tree_widget = BookTreeWidget()
        self.tree_widget.selectionChanged = self.selectionChanged
        self.addWidget(self.tree_widget)

        self.info_widget = InfoWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.resize(800, 600)
        self.addWidget(scroll_area)

    def selectionChanged(self, new, old):
        self.info_widget.set_info(self.tree_widget.currentItem().info)

    def add_items(self):
        for file in self.files:
            info = BookInfo(file)

            if self.calibre_db:
                try:
                    info.calibre = self.calibre_db[info.ISBN]
                except (KeyError, AttributeError):
                    pass

            self.tree_widget.add_item(info)


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

    class FileTreeWidget(QTreeWidget):
        class AuthorItem(QTreeWidgetItem):
            def __init__(self, parent, name):
                super(BookBrowserWidget.FileTreeWidget.AuthorItem, self).__init__(parent)
                self.setText(0, name)
                self.sort_text = ' '.join([name.split(" ")[-1],  name])

            def __lt__(self, other):
                return self.sort_text < other.sort_text

        class Item(QTreeWidgetItem):
            def __init__(self, parent, file):
                super(BookBrowserWidget.FileTreeWidget.Item, self).__init__(parent)
                self.file = file
                self.setText(0, file.title)

        def __init__(self, files, default_pixmap, **kwargs):
            super(BookBrowserWidget.FileTreeWidget, self).__init__(**kwargs)
            self.setColumnCount(1)
            header = QTreeWidgetItem(["Author"])
            self.setHeaderItem(header)
            root = QTreeWidgetItem(self, ["Authors"])
            root.setExpanded(True)
            for name in files.keys():
                name_item = BookBrowserWidget.FileTreeWidget.AuthorItem(root, name)
                for file in files[name]:
                    file_item = BookBrowserWidget.FileTreeWidget.Item(name_item, file)
                    pixmap = QPixmap()
                    try:
                        pixmap = QPixmap()
                        pixmap.loadFromData(file.cover_image)
                    except AttributeError:
                        pixmap = default_pixmap

                    #  af, ar, bg, bn, ca, cs, cy, da, de, el,
                    #  en, es, et, fa, fi, fr, gu, he, hi, hr,
                    #  hu, id, it, ja, kn, ko, lt, lv, mk, ml,
                    #  mr, ne, nl, no, pa, pl, pt, ro, ru, sk,
                    #  sl, so, sq, sv, sw, ta, te, th, tl, tr,
                    #  uk, ur, vi, zh-cn, zh-tw
                    pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(file.language[0]))
                    file_item.setIcon(0, QIcon(pixmap))
            self.sortByColumn(0, Qt.AscendingOrder)