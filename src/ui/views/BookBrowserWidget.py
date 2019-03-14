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
from src.bookinfo.ebook import BookInfo
from src.ui.views.BookTreeView import BookTreeView
from src.ui.views.InfoWidget import InfoWidget

config = AppState().config

class QThread1(QtCore.QThread):
    sig1 = Signal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        self.running = True
        while self.running:
            self.sig1.emit(str(datetime.now()))
            time.sleep(1)
# Subclassing QObject and using moveToThread
# http://blog.qt.digia.com/blog/2007/07/05/qthreads-no-longer-abstract
class Worker(QObject):
    count = 4
    info = Signal(str)
    finished = Signal()

    def __init__(self, input, parent=None):
        QObject.__init__(self, parent)
        self.input = input

    def run(self):
        self.count += 1
        self.info.emit(self.input + str(self.count))
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
        self.populate()

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
        self.worker = Worker('worker..')
        self.start_button = QPushButton("⯈")
        self.start_button.clicked.connect(self.start_thread)
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

    def start_thread(self):
        self.thread = QtCore.QThread()
        self.worker.finished.connect(self.thread.quit)
        self.worker.info.connect(self.on_info)
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.stop_thread)
        self.thread.start()

    def start_thread1(self):
        self.parent().set_status(str(datetime.now()))
        self.thread1 = QThread1()
        self.thread1.start()
        self.thread1.sig1.connect(self.on_info)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_thread(self):
        try:
            self.thread1.running = False
        except:
            pass
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def on_info(self, info):
        print(info)
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
        self.book_tree_view.clear()
        for database in self.files.values():
            for file in database:
                self.add_item(file)
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

    def add_item(self, file):
        self.parent().set_status('Adding {}'.format(file))

        info = BookInfo(file)

        try:
            info.calibre = self.calibre_db[info.ISBN]
        except (KeyError, AttributeError) as kae:
            BookBrowserWidget.logger.debug(kae)

        self.book_tree_view.add_item(info)
        self.book_tree_view.model().sort(2)
        self.book_tree_view.resizeColumnToContents(0)
        self.book_tree_view.hideColumn(2)

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
        settings = QSettings()
        for database in json.loads(settings.value('databases', '[]')):
            self.append_database(database)
        self.populate()