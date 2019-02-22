import logging
import confuse
from xdg import BaseDirectory

string_level_to_int = {
    'DEBUG' : 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50
}
def log_level(level):
    try:
        return string_level_to_int[level]
    except KeyError:
        pass
    try:
        return string_level_to_int[level.upper()]
    except KeyError:
        return 0




class AppState:
    _dict = {}

    def __init__(self):
        self.__dict__ = self._dict
        if not self._dict:
            self.config = confuse.Configuration('BookinS', 'config')
            #logging.basicConfig(format=self.config['logging']['format'].get())
            # logging.getLogger().setLevel(20)
            for key in self.config['logging']['level'].keys():
                try:
                    logging.getLogger(key).setLevel(log_level(self.config['logging']['level'][key].as_str()))
                except confuse.ConfigTypeError:
                    logging.getLogger(key).setLevel(self.config['logging']['level'][key].get())



if __name__ == '__main__':
    print('xdg_cache_home: {}'.format(BaseDirectory.xdg_cache_home))
    print('xdg_data_home: {}'.format(BaseDirectory.xdg_data_home))
    print('xdg data path: {}'.format(BaseDirectory.save_data_path('BookinS/ebooks')))
