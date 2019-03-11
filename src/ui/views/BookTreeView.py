import logging

from PySide2.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PySide2.QtGui import QPixmap, QIcon, QStandardItemModel, \
    QStandardItem
from PySide2.QtWidgets import QTreeView


class AuthorItem():
    def __init__(self, parent, name):
        sort_text = ' '.join([name.split(" ")[-1], name])
        self.item = QStandardItem(name)
        self.item.info = self
        items = [self.item, QStandardItem(''), QStandardItem(sort_text)]
        parent.appendRow(items)

    def appendRow(self, items):
        self.item.appendRow(items)

    def __lt__(self, other):
        return self.sort_text < other.sort_text


class BookItem():
    def __init__(self, parent, info):
        pixmap = QPixmap("../resources/icons/{}-flag-small.png".format(info.language[0]))
        item = QStandardItem(info.title)
        item.setIcon(QIcon(pixmap))
        item.info = info
        publication = str(info.publication_date())
        items = [item, QStandardItem(publication), QStandardItem(publication+info.title)]
        parent.appendRow(items)


def last_first(name):
    return ' '.join([name.split(" ")[-1], name])


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self):
        super(SortFilterProxyModel, self).__init__()

    def itemFromIndex(self, index: QModelIndex):
        item = index.model().itemFromIndex(self.mapToSource(index))
        print(self.sourceModel(), index.model(), item)

        return item

    def lessThan(self, source_left: QModelIndex, source_right: QModelIndex):
        return last_first(source_left.data()) < last_first(source_right.data())



class BookTreeView(QTreeView):
    def __init__(self, **kwargs):
        super(BookTreeView, self).__init__(**kwargs)
        self.item_model = QStandardItemModel()
        headerLabels = ["Name", "Date", "Sort Column"]
        self.item_model.setHorizontalHeaderLabels(headerLabels)
        self.authors = {}
        use_proxy = False
        if use_proxy:
            proxy = SortFilterProxyModel()
            self.setSortingEnabled(True)
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

        except (AttributeError, KeyError) as e:
            logger = logging.getLogger('bookinfo')
            logger.debug('Cannot add item {}'.format(str(info)))
            logger.error(e)
