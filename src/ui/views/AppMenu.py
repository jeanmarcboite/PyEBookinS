from PySide2.QtGui import QIcon, QWindow
from PySide2.QtWidgets import QAction, QFileDialog

File = 'File'

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
        self.triggered.connect(Action.default)


class checkableAction(qAction):
    def __init__(self, *args, **kwargs):
        super(checkableAction, self).__init__(*args, **kwargs)
        self.setCheckable(True)

    def set_default(self):
        self.triggered.connect(Action.checkable)


class Action:
    _dict = {}

    def __init__(self):
        self.__dict__ = self._dict

    @classmethod
    def append_database(cls):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        filenames = []

        if dialog.exec_():
            filenames = dialog.selectedFiles()
            action = Action()
            for filename in filenames:
                action.window.browser.append_database(filename)
                delete = action.window.menuBar().menu['File'].menu['delete']
                qdelete = delete.addAction(qIcon('Misc-Delete-Database-icon.png'),
                                           filename)
                qdelete.triggered.connect(lambda: action.remove_database(filename))

    def remove_database(self, filename: str):
        self.window.browser.remove_database(filename)
        self.update()

    def update(self):
        delete = self.window.menuBar().menu['File'].menu['delete']
        delete.clear()
        for file in self.window.browser.files:
            qdelete = delete.addAction(QIcon('../resources/icons/Misc-Delete-Database-icon.png'),
                                       file)
            qdelete.triggered.connect(lambda: self.remove_database(file))

    @classmethod
    def clear(cls):
        Action().window.browser.clear()
        Action().update()

    @classmethod
    def quit(cls):
        Action().window.close()

    @classmethod
    def default(cls):
        print('default')

    @classmethod
    def checkable(cls, action):
        print('checkable', action)

    @classmethod
    def funWithParams(cls, *args):
        print(args)


applicationMenu = {
    'File': [qAction('Misc-New-Database-icon.png',
                     'Add', 'add directory', 'Ctrl+A', Action.append_database),
             {'delete': []},
             qAction('Actions-edit-clear-icon.png',
                     'Clear', 'remove all directories', func=Action.clear),
             qAction('Actions-application-exit-icon.png',
                     'Quit', func=Action.quit),
             ],
    'View': [checkableAction(None, 'check')],
    'Subs': [
        qAction(None, 'Params', func=(lambda action='yy', arg='xx': Action.funWithParams(action, arg))),
        checkableAction(None, 'check'),
        {'SubSub': [
            checkableAction(None, 'check'),
            {'subsubsub': [qAction('Open-folder-add-icon.png',
                                   'Add', 'add directory', 'Ctrl+A', Action.append_database)]}
        ]}
    ]
}


def add_menu(menuBar, menu):
    menuBar.menu = {}
    for key in menu.keys():
        submenu = menuBar.addMenu(key)
        menuBar.menu[key] = submenu
        for action in menu[key]:
            if isinstance(action, dict):
                add_menu(submenu, action)
            else:
                submenu.addAction(action)
                action.set_widgets()


def add_menus(window: QWindow, menu=applicationMenu):
    add_menu(window.menuBar(), menu)

    Action().window = window
    Action().update()
