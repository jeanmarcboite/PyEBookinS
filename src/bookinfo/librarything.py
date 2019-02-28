import urllib
import xml.etree.ElementTree as ElementTree

import requests
from bs4 import BeautifulSoup
from joblib import Memory

from config import AppState

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())


# <author id="72" authorcode="woolfvirginia">Virginia Woolf</author>
# <title>Mrs. Dalloway</title>
# <rating>7.8</rating>
# <url>http://www.librarything.com/work/4890</url>

class Librarything(dict):
    xmlns = '{http://www.librarything.com/}'
    attributes = {
        'item': [
            'author', 'title', 'rating', 'url', 'commonknowledge'
        ]
    }

    def __init__(self, root=None):
        super(Librarything, self).__init__()
        if root:
            for key in Librarything.attributes.keys():
                for subkey in Librarything.attributes[key]:
                    field = root.find("{}{}/{}{}".format(Librarything.xmlns, key, Librarything.xmlns, subkey))
                    if (field is not None):
                        self[subkey] = field.text
            self.url = self['url']


@memory.cache()
def ebook_librarything_response(isbn, id_type):
    url = config['librarything']['url'][id_type].as_str().format(isbn,
                                                                 config['librarything']['key'].get())
    return requests.get(url)


def librarything_from(librarything_response):
    ltml = None
    if librarything_response.ok:
        with open('/home/box/tmp/librarything', 'w') as output_file:
            output_file.write(librarything_response.content.decode("utf-8"))
        root = ElementTree.fromstring(librarything_response.content)
        return Librarything(root.find('{http://www.librarything.com/}ltml'))
    return Librarything()


def librarything_from_isbn(isbn):
    return librarything_from(ebook_librarything_response(isbn, 'isbn'))


def librarything_from_id(id):
    return librarything_from(ebook_librarything_response(id, 'id'))

@memory.cache()
def librarything_cover(url):
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')
        for meta in soup.find_all('meta'):
            if meta.get('property') == 'og:image':
                return urllib.request.urlopen(meta.get('content')).read()
