import os
from glob import glob
from pprint import pformat
from copy import copy

from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QWidget, QHBoxLayout, QListWidget, QStackedWidget, QListWidgetItem, QLabel
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem

from src.bookinfo.ebook import epub_info
from src.bookinfo.goodreads import goodreads_from_isbn
from src.config import Config

class BookBrowserWidget(QWidget):

    def __init__(self, dirpath, parent=None):
        super(BookBrowserWidget, self).__init__(parent)

        files = BookBrowserWidget.find_files(dirpath)

        bookIcon = QPixmap("../resources/icons/iconfinder_book_285636.png")

        self.setLayout(QHBoxLayout())
        self.left_widget = BookBrowserWidget.FileTreeWidget(BookBrowserWidget.files_by(files, 'author'), bookIcon)
        self.left_widget.selectionChanged = self.selectionChanged
        self.layout().addWidget(self.left_widget)

        self.right_widget = QWidget()
        self.right_widget.setLayout(QHBoxLayout())
        self.right_widget.layout().addWidget(QLabel('no selection'))
        self.layout().addWidget(self.right_widget)

    def clean(self):
        while 1:
            child = self.right_widget.layout().takeAt(0)
            if not child:
                break
            child.widget().deleteLater()

    def selectionChanged(self, new, old):
        print(self.left_widget.currentItem())
        try:
            print(self.left_widget.currentItem().file['title'])
            self.clean()
            info = copy(self.left_widget.currentItem().file)
            del info['cover_image']
            self.right_widget.layout().addWidget(QLabel(pformat(info)))
        except AttributeError:
            pass

    @staticmethod
    def find_files(dirpath, extensions = Config.book_extensions):
        files = []
        for extension in extensions:
            pattern = os.path.join(dirpath, '*.%s' %extension)
            files.extend(glob(pattern))
        return files
    @staticmethod
    def files_by(files, key):
        authors = dict()
        for file in files:
            info = epub_info(file)
            if info[key] not in authors.keys():
                authors[info[key]] = []
            authors[info[key]].append(info)
        return authors
    @staticmethod
    def stacked_widget(files):
        widget = QStackedWidget()
        for file in files:
            #widget.addWidget(EPubWidget(book_path=file))
            pass

        return widget

    class FileListWidget(QListWidget):
        def __init__(self, files, bookIcon, **kwargs):
            super(BookBrowserWidget.FileListWidget, self).__init__(**kwargs)
            for file in files:
                info = epub_info(file)
                # pprint(goodreads_from_isbn(info['isbn']))
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
        def __init__(self, files, bookIcon, **kwargs):
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
                        pixmap = bookIcon
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


        def selectionChanged(self, new, old):
            print("selectionChanged:", new, old)
            print(new.indexes())
            print(self.currentItem().file)
            print(self.selectedItems())

