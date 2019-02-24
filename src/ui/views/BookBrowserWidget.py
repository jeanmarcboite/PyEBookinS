import os
from glob import glob
from pathlib import Path

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QScrollArea, \
    QSplitter
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem

from config import AppState
from src.bookinfo.calibredb import *
from src.bookinfo.ebook import book_info
from src.ui.views.InfoWidget import InfoWidget


# noinspection PyPep8Naming
class BookBrowserWidget(QSplitter):

    def __init__(self, dirpath, parent=None):
        super(BookBrowserWidget, self).__init__(Qt.Horizontal, parent)

        files = BookBrowserWidget.find_files(dirpath)

        db = os.path.join(dirpath, 'no-metadata.db')
        calibre_db = None
        if os.path.isfile(db):
            calibre_db = CalibreDB(database='sqlite:///' + db)

        default_pixmap = QPixmap("../resources/icons/iconfinder_book_285636.png")

        self.tree_widget = BookBrowserWidget.FileTreeWidget(BookBrowserWidget.files_by(files, 'author', calibre_db),
                                                            default_pixmap)
        self.tree_widget.selectionChanged = self.selectionChanged
        self.addWidget(self.tree_widget)

        self.info_widget = InfoWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.resize(800, 600)
        self.addWidget(scroll_area)

    def selectionChanged(self, new, old):
        self.info_widget.set_info(self.tree_widget.currentItem().file)

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
            info = book_info(file, calibre_db)
            attr = getattr(info, key)
            if attr not in by.keys():
                by[attr] = []
            by[attr].append(info)
        return by

    class FileTreeWidget(QTreeWidget):
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
                name_item = QTreeWidgetItem(root, [name])
                for file in files[name]:
                    file_item = BookBrowserWidget.FileTreeWidget.Item(name_item, file)
                    pixmap = QPixmap()
                    if 'cover_image' not in file.keys():
                        pixmap = default_pixmap
                    else:
                        pixmap = QPixmap()
                        pixmap.loadFromData(file.cover_image)

                    #  af, ar, bg, bn, ca, cs, cy, da, de, el,
                    #  en, es, et, fa, fi, fr, gu, he, hi, hr,
                    #  hu, id, it, ja, kn, ko, lt, lv, mk, ml,
                    #  mr, ne, nl, no, pa, pl, pt, ro, ru, sk,
                    #  sl, so, sq, sv, sw, ta, te, th, tl, tr,
                    #  uk, ur, vi, zh-cn, zh-tw
                    pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(file.language[0]))
                    file_item.setIcon(0, QIcon(pixmap))
