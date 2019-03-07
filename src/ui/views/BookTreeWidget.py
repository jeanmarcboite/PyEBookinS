from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem
import logging

class BookTreeWidget(QTreeWidget):
    class AuthorItem(QTreeWidgetItem):
        def __init__(self, parent, name):
            super(BookTreeWidget.AuthorItem, self).__init__(parent)
            self.setText(0, name)
            self.sort_text = ' '.join([name.split(" ")[-1], name])

        def __lt__(self, other):
            return self.sort_text < other.sort_text

    class Item(QTreeWidgetItem):
        def __init__(self, parent, info):
            super(BookTreeWidget.Item, self).__init__(parent)
            self.info = info
            self.setText(0, info.title)

    def __init__(self, **kwargs):
        super(BookTreeWidget, self).__init__(**kwargs)
        self.setColumnCount(1)
        header = QTreeWidgetItem(["Author"])
        self.setHeaderItem(header)
        self.root = QTreeWidgetItem(self, ["Authors"])
        self.root.setExpanded(True)
        self.authors = {}
        self.sortByColumn(0, Qt.AscendingOrder)

    def add_item(self, info):
        try:
            info.title
            try:
                author_item = self.authors[info.author]
            except KeyError:
                author_item = BookTreeWidget.AuthorItem(self.root, info.author)
                self.authors[info.author] = author_item
            info_item = BookTreeWidget.Item(author_item, info)
            pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(info.language[0]))
            info_item.setIcon(0, QIcon(pixmap))
        except (AttributeError, KeyError) as e:
            logger = logging.getLogger('bookinfo')
            logger.debug('Cannot add item {}'.format(str(info)))
            logger.error(e)

