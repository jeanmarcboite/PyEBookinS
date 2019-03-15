import logging
import os
import json
from datetime import datetime
import time
from pathlib import Path

from PySide2 import QtCore
from PySide2.QtCore import Qt, QModelIndex, QSettings, Signal, Slot, QObject
from PySide2.QtWidgets import QScrollArea, \
    QSplitter, QFrame, QVBoxLayout, QPushButton, QHBoxLayout
from xdg import BaseDirectory

from config import AppState
from src.bookinfo.calibredb import CalibreDB
from src.bookinfo.ebook import BookInfo, book_info
from src.ui.views.AppMenu import AppMenu
from src.ui.views.BookTreeView import BookTreeView
from src.ui.views.InfoWidget import InfoWidget

config = AppState().config


class Worker(QObject):
    info = Signal(str)
    finished = Signal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.files = []

    def run(self):
        for file in self.files:
            book_info(file)
            self.info.emit(str(file))
        self.finished.emit()


# noinspection PyPep8Naming
class BookBrowserWidget(QSplitter):
    logger = logging.getLogger('gui')

    def __init__(self, parent=None):
        super(BookBrowserWidget, self).__init__(Qt.Horizontal, parent)

        self.files = {}
        self.calibre = {}

        self.book_tree_view = self.add_book_tree_view()

        self.info_widget = self.add_info_widget()

        self.set_sizes()
        self.splitterMoved.connect(self.splitter_moved)

        self.worker = Worker()
        self.thread = QtCore.QThread()

        self.enable_add = True
        self.set_databases()

    def append_database(self, database: str):
        self.files[database] = []
        if os.path.isfile(database):
            self.files[database] = [database]
        elif os.path.isdir(database):
            self.files[database] = BookBrowserWidget.find_files(database)
            calibre = os.path.join(database, 'metadata.db')
            if os.path.isfile(calibre):
                self.calibre[database] = CalibreDB(database='sqlite:///' + calibre)

        BookBrowserWidget.logger.info("Import %d files", len(self.files[database]))

    def remove_database(self, database: str):
        del self.files[database]
        self.populate()

    @staticmethod
    def add_calibre_db():
        try:
            calibre = config['calibre'].as_str()
            if not os.path.exists(calibre):
                calibre = BaseDirectory.save_data_path('{}/{}'.format(config['application_name'],
                                                                      calibre))
            if os.path.isdir(calibre):
                calibre = os.path.join(calibre, 'metadata.db')

            if os.path.isfile(calibre):
                return CalibreDB(database='sqlite:///' + calibre)
        except AttributeError:
            return None
        return None

    def add_book_tree_view(self):
        frame = QFrame()
        frame.setLayout(QVBoxLayout())
        buttons = QHBoxLayout()

        self.start_button = QPushButton("⯈")
        #self.start_button.clicked.connect(self.start_thread)
        buttons.addWidget(self.start_button)
        self.stop_button = QPushButton("⯀")
        self.stop_button.clicked.connect(self.stop_thread)
        buttons.addWidget(self.stop_button)
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        frame.layout().addLayout(buttons)

        book_tree_view = BookTreeView()
        book_tree_view.clicked[QModelIndex].connect(self.item_selected)
        frame.layout().addWidget(book_tree_view)
        self.addWidget(frame)

        return book_tree_view

    def stop_thread(self):
        print('stop thread')
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def on_info(self, info):
        self.parent().set_status(str(info))

    def add_info_widget(self):
        info_widget = InfoWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.resize(800, 600)
        self.addWidget(scroll_area)

        return info_widget

    def clear(self):
        self.book_tree_view.clear()
        files = self.files
        self.files = {}
        return files

    def populate(self):
        self.enable_add = False
        self.book_tree_view.clear()

        files = []
        for database in self.files.values():
            files.extend(database)
        self.worker.files = files
        self.worker.moveToThread(self.thread)
        self.worker.info.connect(self.on_item_available)
        self.worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.on_thread_finished())
        AppMenu().enable_add(self.enable_add)
        self.thread.start()

        settings = QSettings()
        settings.setValue('databases', json.dumps([file for file in self.files]))
        # self.book_tree_view.read_expanded_items()

    def item_selected(self, index):
        if (index.parent().row() < 0):
            item = index.model().item(index.row())
            self.info_widget.set_author_info(item.info.wikipedia())
        else:
            parent_item = index.model().item(index.parent().row())
            item = parent_item.child(index.row())
            self.info_widget.set_book_info(item.info)

    def on_thread_finished(self):
        self.logger.debug('thread finished')
        print('thread fini')
        self.enable_add = True
        AppMenu().enable_add(self.enable_add)

    def on_item_available(self, file):
        print('got', file)
        info = BookInfo(file)

        try:
            info.calibre = self.calibre_db[info.ISBN]
        except (KeyError, AttributeError) as kae:
            BookBrowserWidget.logger.debug(kae)

        self.book_tree_view.add_item(info)
        self.book_tree_view.model().sort(2)
        self.book_tree_view.resizeColumnToContents(0)
        self.book_tree_view.hideColumn(2)
        self.repaint()

    @staticmethod
    def find_files(dirpath, extensions=AppState().config['ebook_extensions'].get()):
        files = []
        for extension in extensions:
            files.extend(Path(dirpath).glob('**/*.' + extension))
        return files

    def splitter_moved(self):
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        settings.setValue('sizes', self.sizes())
        settings.endGroup()

    def set_sizes(self):
        settings = QSettings()
        settings.beginGroup(self.__class__.__name__)
        sizes = settings.value('sizes', [])
        if sizes and type(sizes) is list:
            self.setSizes(list(map(int, sizes)))
        settings.endGroup()

    def set_databases(self):
        print('set databases')
        settings = QSettings()
        for database in json.loads(settings.value('databases', '[]')):
            self.append_database(database)
        self.populate()