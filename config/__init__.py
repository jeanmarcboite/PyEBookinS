import logging
import sys

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
            # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
            #                   format='%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s')
            for key in self.config['logging']['level'].keys():
                try:
                    # create logger
                    log = logging.getLogger(key)
                    log.setLevel(log_level(self.config['logging']['level'][key].as_str()))

                    # create formatter and add it to the handlers
                    formatter = logging.Formatter('%(asctime)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s')

                    # create file handler which logs even debug messages
                    fh = logging.FileHandler('{}.log'.format(key))
                    fh.setLevel(logging.DEBUG)
                    fh.setFormatter(formatter)
                    log.addHandler(fh)

                    # create console handler with a higher log level
                    ch = logging.StreamHandler()
                    ch.setLevel(log_level(self.config['logging']['level'][key].as_str()))
                    ch.setFormatter(formatter)
                    log.addHandler(ch)
                except confuse.ConfigTypeError:
                    logging.getLogger(key).setLevel(self.config['logging']['level'][key].get())



if __name__ == '__main__':
    print('xdg_cache_home: {}'.format(BaseDirectory.xdg_cache_home))
    print('xdg_data_home: {}'.format(BaseDirectory.xdg_data_home))
    print('xdg data path: {}'.format(BaseDirectory.save_data_path('BookinS/ebooks')))
