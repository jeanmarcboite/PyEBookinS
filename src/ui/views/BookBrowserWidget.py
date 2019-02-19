import os
from glob import glob
from pprint import pformat
from copy import copy

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem, QLabel, QScrollArea, \
    QSplitter
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem

from src.bookinfo.ebook import epub_info
from src.bookinfo.goodreads import goodreads_from_isbn
from src.bookinfo.librarything import librarything_from_isbn
from config import AppState
from src.bookinfo.calibredb import *

class BookBrowserWidget(QSplitter):

    def __init__(self, dirpath, parent=None):
        super(BookBrowserWidget, self).__init__(Qt.Horizontal, parent)

        files = BookBrowserWidget.find_files(dirpath)

        db = os.path.join(dirpath, 'no-metadata.db')
        calibre_db = None
        if os.path.isfile(db):
            calibre_db = CalibreDB(database='sqlite:///' + db)


        default_pixmap = QPixmap("../resources/icons/iconfinder_book_285636.png")

        self.tree_widget = BookBrowserWidget.FileTreeWidget(BookBrowserWidget.files_by(files, 'author', calibre_db), default_pixmap)
        self.tree_widget.selectionChanged = self.selectionChanged
        self.addWidget(self.tree_widget)

        self.info_widget = BookBrowserWidget.InfoWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.info_widget)
        scroll_area.setWidgetResizable(True)
        self.addWidget(scroll_area)

    class InfoWidget(QWidget):
        def __init__(self, parent=None):
            super(BookBrowserWidget.InfoWidget, self).__init__(parent)
            self.setLayout(QHBoxLayout())
            self.layout().addWidget(QLabel('no selection'))

        def clean(self):
            while True:
                child = self.layout().takeAt(0)
                if child:
                    child.widget().deleteLater()
                else:
                    break

        def setWidget(self, widget):
            self.clean()
            self.layout().addWidget(widget)

    def selectionChanged(self, new, old):
        try:
            print('select ', self.tree_widget.currentItem().file['title'])
            info = copy(self.tree_widget.currentItem().file)
            del info['cover_image']
            self.info_widget.setWidget(QLabel(pformat(info)))
        except AttributeError:
            pass

    @staticmethod
    def find_files(dirpath, extensions=AppState().config['ebook_extensions'].get()):
        files = []
        for extension in extensions:
            pattern = os.path.join(dirpath, '*.' + extension)
            files.extend(glob(pattern))
        return files
    @staticmethod
    def files_by(files, key, calibre_db=None):
        by = dict()
        for file in files:
            info = epub_info(file, calibre_db)
            if info[key] not in by.keys():
                by[info[key]] = []
            by[info[key]].append(info)
        return by

    class FileListWidget(QListWidget):
        def __init__(self, files, calibre_db, bookIcon, **kwargs):
            super(BookBrowserWidget.FileListWidget, self).__init__(**kwargs)
            for file in files:
                info = epub_info(file, calibre_db)
                info['calibre'] = calibre_db[info['isbn']]
                widget = BookBrowserWidget.FileListWidget.ItemWidget(bookIcon, info['title'])
                widgetItem = QListWidgetItem(self)
                widgetItem.setSizeHint(widget.sizeHint())
                self.addItem(widgetItem)
                self.setItemWidget(widgetItem, widget)

        class ItemWidget(QWidget):
            def __init__(self, icon, text, **kwargs):
                super(BookBrowserWidget.FileListWidget.ItemWidget, self).__init__(**kwargs)
                layout = QHBoxLayout()
                iconLabel = QLabel()
                iconLabel.setPixmap(icon.scaledToHeight(24))
                label = QLabel(text)
                layout.addWidget(iconLabel, 0)
                layout.addWidget(label, 1)
                self.setLayout(layout)

    class FileTreeWidget(QTreeWidget):
        class Item(QTreeWidgetItem):
            def __init__(self, parent, file):
                super(BookBrowserWidget.FileTreeWidget.Item, self).__init__(parent)
                self.file = file
                self.setText(0, file['title'])

        def __init__(self, files, default_pixmap, **kwargs):
            super(BookBrowserWidget.FileTreeWidget, self).__init__(**kwargs)
            self.setColumnCount(1)
            header = QTreeWidgetItem(["Author"])
            self.setHeaderItem(header)
            root = QTreeWidgetItem(self, ["Authors"])
            root.setExpanded(True)
            for name in files.keys():
                name_item = QTreeWidgetItem(root, [name])
                for file in files[name]:
                    file_item = BookBrowserWidget.FileTreeWidget.Item(name_item, file)
                    pixmap = QPixmap()
                    if 'cover_image' not in file.keys():
                        pixmap = default_pixmap
                    else:
                        pixmap = QPixmap()
                        pixmap.loadFromData(file['cover_image'])

                     #  af, ar, bg, bn, ca, cs, cy, da, de, el,
#  en, es, et, fa, fi, fr, gu, he, hi, hr,
#  hu, id, it, ja, kn, ko, lt, lv, mk, ml,
#  mr, ne, nl, no, pa, pl, pt, ro, ru, sk,
#  sl, so, sq, sv, sw, ta, te, th, tl, tr,
#  uk, ur, vi, zh-cn, zh-tw
                    pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(file['language'][0]))
                    file_item.setIcon(0, QIcon(pixmap))
