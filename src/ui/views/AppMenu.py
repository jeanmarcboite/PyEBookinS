from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QFileDialog

File = 'File'

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
            self.setIcon(QIcon('../resources/icons/' + self._icon))
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
    def add_directory(cls):
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        filenames = []

        if dialog.exec_():
            filenames = dialog.selectedFiles()
        print(filenames)


    @classmethod
    def delete_directory(cls):
        print('delete')

    @classmethod
    def clear(cls):
        print('clear')

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
                 'Add', 'add directory', 'Ctrl+A', Action.add_directory),
             {'delete': [
                 qAction('Misc-Delete-Database-icon.png',
                         'Delete', 'delete directory', func=Action.delete_directory),

             ]},
       qAction('Actions-edit-clear-icon.png',
                     'Clear', 'remove all directories', func=Action.clear),
        qAction('Actions-application-exit-icon.png',
                     'Quit'),
    ],
    'View': [checkableAction(None, 'check')],
    'Subs': [
        qAction(None, 'Params', func=(lambda action='yy', arg='xx': Action.funWithParams(action,arg))),
        checkableAction(None, 'check'),
        {'SubSub': [
            checkableAction(None, 'check'),
            {'subsubsub': [qAction('Open-folder-add-icon.png',
                 'Add', 'add directory', 'Ctrl+A', Action.add_directory)]}
        ]}
    ]
}


def add_menu(menuBar, menu=applicationMenu):
    for key in menu.keys():
        submenu = menuBar.addMenu(key)
        for action in menu[key]:
            if isinstance(action, dict):
                add_menu(submenu, action)
            else:
                submenu.addAction(action)
                action.set_widgets()