import logging

from PySide2.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PySide2.QtGui import QPixmap, QIcon, QStandardItemModel, \
    QStandardItem
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
        super(BookItem, self).__init__(info.title_and_publication_date())
        self.info = info
        parent.appendRow(self)


def last_first(name):
    return ' '.join([name.split(" ")[-1], name])


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(SortFilterProxyModel, self).__init__()

    def itemFromIndex(self, index):
        return self.sourceModel().itemFromIndex(self.mapToSource(index))

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        return last_first(source_left.data()) < last_first(source_right.data())



class BookTreeView(QTreeView):
    def __init__(self, **kwargs):
        super(BookTreeView, self).__init__(**kwargs)
        self.item_model = QStandardItemModel()
        self.item_model.setHorizontalHeaderLabels(["Author"])
        self.authors = {}
        self.sortByColumn(0, Qt.AscendingOrder)
        self.setSortingEnabled(True)
        use_proxy = True
        if use_proxy:
            proxy = SortFilterProxyModel()
            proxy.setSourceModel(self.item_model)
            self.setModel(proxy)
        else:
            self.setModel(self.item_model)

    def add_item(self, info):
        try:
            info.title
            try:
                author_item = self.authors[info.author]
            except KeyError:
                author_item = AuthorItem(self.item_model.invisibleRootItem(),
                                         info.author)
                author_item.wikipedia = 'https://en.wikipedia.org/wiki/{}'.format('_'.join(info.author.split()))
                self.authors[info.author] = author_item
            info_item = BookItem(author_item, info)
            pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(info.language[0]))
            info_item.setIcon(QIcon(pixmap))
        except (AttributeError, KeyError) as e:
            logger = logging.getLogger('bookinfo')
            logger.debug('Cannot add item {}'.format(str(info)))
            logger.error(e)
