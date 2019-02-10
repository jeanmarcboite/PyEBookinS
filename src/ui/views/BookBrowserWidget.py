import os
from glob import glob
from pprint import pprint

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
        list_widget = BookBrowserWidget.FileListWidget(files, bookIcon)
        stacked_widget = self.stacked_widget(files)
        list_widget.currentRowChanged.connect(lambda i: stacked_widget.setCurrentIndex(i))

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(list_widget)

        right_widget = BookBrowserWidget.FileTreeWidget(files, bookIcon)
        self.layout().addWidget(right_widget)

    @staticmethod
    def find_files(dirpath, extensions = Config.book_extensions):
        files = []
        for extension in extensions:
            pattern = os.path.join(dirpath, '*.%s' %extension)
            files.extend(glob(pattern))
        return files

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
                pprint(goodreads_from_isbn(info['isbn']))
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
        def __init__(self, files, bookIcon, **kwargs):
            super(BookBrowserWidget.FileTreeWidget, self).__init__(**kwargs)
            header = QTreeWidgetItem(["Virtual folder tree","Comment"])
            # self.setHeader(header)
            root = QTreeWidgetItem(self, ["Untagged files"])
            item1 = QTreeWidgetItem(root, ["child 1"])
            item11 = QTreeWidgetItem(item1, ["child 1 1"])
            item2 = QTreeWidgetItem(root, ["child 2"])
