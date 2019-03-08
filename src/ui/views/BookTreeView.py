import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QIcon, QStandardItemModel, QStandardItem
from PySide2.QtWidgets import QTreeView


class AuthorItem(QStandardItem):
    def __init__(self, parent, name):
        super(AuthorItem, self).__init__(name)
        self.sort_text = ' '.join([name.split(" ")[-1], name])
        parent.appendRow(self)

    def __lt__(self, other):
        return self.sort_text < other.sort_text


class BookItem(QStandardItem):
    def __init__(self, parent, info):
        super(BookItem, self).__init__(info.title)
        self.info = info
        parent.appendRow(self)


class BookTreeView(QTreeView):
    def __init__(self, **kwargs):
        super(BookTreeView, self).__init__(**kwargs)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Author"])
        self.authors = {}
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setModel(model)

    def add_item(self, info):
        try:
            info.title
            try:
                author_item = self.authors[info.author]
            except KeyError:
                author_item = AuthorItem(self.model().invisibleRootItem(), info.author)
                self.authors[info.author] = author_item
            info_item = BookItem(author_item, info)
            pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(info.language[0]))
            info_item.setIcon(QIcon(pixmap))
        except (AttributeError, KeyError) as e:
            logger = logging.getLogger('bookinfo')
            logger.debug('Cannot add item {}'.format(str(info)))
            logger.error(e)
