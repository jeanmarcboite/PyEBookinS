import json
from functools import partial

from PySide2.QtCore import QSettings
from PySide2.QtGui import QIcon, QWindow
from PySide2.QtWidgets import QAction, QFileDialog


class qIcon(QIcon):
    def __init__(self, icon, **kwargs):
        super(qIcon, self).__init__('../resources/icons/' + icon, **kwargs)


class qAction(QAction):
    def __init__(self, icon, text, tooltip=None, shortcut=None, func=None, **kwargs):
        super(qAction, self).__init__(text, **kwargs)
        # this = QAction(icon, text, self)
        # icon, tootltip... must be constructed later (after QGuiApplication)
        self._icon = icon
        self._tooltip = tooltip
        self._shortcut = shortcut
        self._func = func

    def set_widgets(self):
        if self._icon:
            self.setIcon(qIcon(self._icon))
        self.setToolTip(self._tooltip)
        if self._shortcut:
            self.setShortcut(self._shortcut)

        if self._func:
            self.triggered.connect(self._func)
        else:
            self.set_default()

    def set_default(self):
        self.triggered.connect(AppMenu.default)


class checkableAction(qAction):
    def __init__(self, *args, **kwargs):
        super(checkableAction, self).__init__(*args, **kwargs)
        self.setCheckable(True)

    def set_default(self):
        self.triggered.connect(AppMenu.checkable)


class AppMenu:
    FILE = 'File'
    ADD = 'Add'
    DELETE = 'Delete'
    RECENT = 'Recent'

    _dict = {
        'recent': set()
    }

    @staticmethod
    def menu_items():
        return {
            AppMenu.FILE: [qAction('Misc-New-Database-icon.png',
                           AppMenu.ADD, 'add directory', 'Ctrl+A', AppMenu.append_database),
                   {AppMenu.DELETE: [],
                    AppMenu.RECENT: []},
                   qAction('Actions-edit-clear-icon.png',
                           'Clear', 'remove all directories', func=AppMenu.clear),
                   qAction('Actions-application-exit-icon.png',
                           'Quit', func=AppMenu.quit),
                   ],
            'View': [checkableAction(None, 'check')],
            'Subs': [
                qAction(None, 'Params', func=(lambda action='yy', arg='xx': AppMenu.funWithParams(action, arg))),
                checkableAction(None, 'check'),
                {'SubSub': [
                    checkableAction(None, 'check'),
                    {'subsubsub': [qAction('Open-folder-add-icon.png',
                                           'Add', 'add directory', 'Ctrl+A', AppMenu.append_database)]}
                ]}
            ]
        }

    def __init__(self):
        self.__dict__ = self._dict

    def add_menu(self, menuBar, menu):
        for key in menu.keys():
            submenu = menuBar.addMenu(key)
            submenu.menu = {}
            menuBar.menu[key] = submenu
            for action in menu[key]:
                if isinstance(action, dict):
                    self.add_menu(submenu, action)
                else:
                    submenu.addAction(action)
                    menuBar.menu[key].menu[action.text()] = action
                    action.set_widgets()

    def init(self, window: QWindow, menu=None):
        if menu is None:
            menu = AppMenu.menu_items()
        window.menuBar().menu = {}
        self.add_menu(window.menuBar(), menu)

        AppMenu().window = window

    def init_databases(self):
        settings = QSettings()
        for database in json.loads(settings.value('recent', '[]')):
            self.add_recent(database)
        self.update()

    @classmethod
    def append_database(cls):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        filenames = []

        if dialog.exec_():
            AppMenu().append_databases(dialog.selectedFiles())

    def append_databases(self, filenames):
        for filename in filenames:
            self.window.browser.append_database(filename)
            self.recent.discard(filename)
        self.window.browser.populate()
        self.update()

    def remove_database(self, filename: str):
        self.window.browser.remove_database(filename)
        self.add_recent(filename)
        self.update()

    def enable_add(self, enable):
        print('set enabled', enable)
        for item in [AppMenu.ADD, AppMenu.DELETE, AppMenu.RECENT]:
            self.window.menuBar().menu[AppMenu.FILE].menu[item].setEnabled(enable)

    def update(self):
        delete = self.window.menuBar().menu[AppMenu.FILE].menu[AppMenu.DELETE]
        delete.clear()
        for file in self.window.browser.files:
            qdelete = delete.addAction(QIcon('../resources/icons/Misc-Delete-Database-icon.png'),
                                       file)
            qdelete.triggered.connect(partial(self.remove_database, file))
        recent = self.window.menuBar().menu[AppMenu.FILE].menu[AppMenu.RECENT]
        recent.clear()
        for file in self.recent:
            qrecent = recent.addAction(qIcon('Folder-Add-icon.png'), file)
            qrecent.triggered.connect(partial(self.append_databases, [file]))
        settings = QSettings()
        settings.setValue('recent', json.dumps([r for r in self.recent]))

    def add_recent(self, file):
        self.recent.add(file)

    @classmethod
    def clear(cls):
        AppMenu().window.browser.clear()
        AppMenu().update()

    @classmethod
    def quit(cls):
        AppMenu().window.close()

    @classmethod
    def default(cls):
        print('default')

    @classmethod
    def checkable(cls, action):
        print('checkable', action)

    @classmethod
    def funWithParams(cls, *args):
        print(args)
