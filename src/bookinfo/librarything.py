import requests
import xml.etree.ElementTree as ElementTree
from joblib import Memory
from config import AppState

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())

# <author id="72" authorcode="woolfvirginia">Virginia Woolf</author>
# <title>Mrs. Dalloway</title>
# <rating>7.8</rating>
# <url>http://www.librarything.com/work/4890</url>

class Librarything():
    xmlns = '{http://www.librarything.com/}'
    attributes = {
       'item': [
            'author', 'title', 'rating', 'url', 'commonknowledge'
        ]
   }

@memory.cache()
def ebook_librarything_response(isbn, id_type):
    url = config['librarything']['url'][id_type].as_str().format(isbn,
                                                config['librarything']['key'].get())
    return requests.get(url)

def librarything_from(librarything_response):
    ltml = None
    if librarything_response.ok:
        with open('/home/box/tmp/librarything', 'w') as output_file:
            output_file.write(librarything_response.content.decode("utf-8") )
        root = ElementTree.fromstring(librarything_response.content)
        ltml = root.find('{http://www.librarything.com/}ltml')
    if ltml:
        librarything = {}
        for key in Librarything.attributes.keys():
            librarything[key] = {}
            for subkey in Librarything.attributes[key]:
                field = ltml.find("{}{}/{}{}".format(Librarything.xmlns, key, Librarything.xmlns, subkey))
                if (field is not None):
                    librarything[key][subkey] = field.text
        return librarything['item']
    return {}

def librarything_from_isbn(isbn):
    return librarything_from(ebook_librarything_response(isbn, 'isbn'))
def librarything_from_id(id):
    return librarything_from(ebook_librarything_response(id, 'id'))
