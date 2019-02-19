import confuse
from xdg import BaseDirectory

class AppState():
    _dict = {}

    def __init__(self):
        self.__dict__ = self._dict
        if not self._dict:
            print('get config')
            self.config = confuse.Configuration('BookinS', 'config')

if __name__ == '__main__':
    print('xdg_data_home: {}'.format(BaseDirectory.xdg_data_home))
    print('xdg data path: {}'.format(BaseDirectory.save_data_path('BookinS/ebooks')))