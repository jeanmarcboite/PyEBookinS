import requests
import xml.etree.ElementTree as ElementTree
from joblib import Memory
from config import AppState

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())


class Goodreads():
    attributes = {
        'book': [
            'id', 'title',
            'description',
            'image_url'
        ],
        'book/work': [
            'id',
            'ratings_sum', 'ratings_count', 'rating_dist'
            'original_publication_year',
            'original_publication_month',
            'original_publication_day',
            'original_title',
        ],
        'book/authors/author': [
            'id', 'name', 'image_url', 'link'
        ]
    }


@memory.cache()
def ebook_goodreads_response(isbn, id_type):
    url = config['goodreads']['url'][id_type].as_str().format(isbn,
                                                config['goodreads']['key'].get())
    return requests.get(url)

def goodreads_from(goodreads_response):
    if goodreads_response.ok:
        with open('/home/box/tmp/goodreads', 'w') as output_file:
            output_file.write(goodreads_response.content.decode("utf-8") )
        root = ElementTree.fromstring(goodreads_response.content)
        goodreads = {}
        for key in Goodreads.attributes.keys():
            goodreads[key] = {}
            for subkey in Goodreads.attributes[key]:
                field = root.find("{}/{}".format(key, subkey))
                if (field is not None):
                    goodreads[key][subkey] = field.text
        return goodreads
    return {}

def goodreads_from_isbn(isbn):
    return goodreads_from(ebook_goodreads_response(isbn, 'isbn'))
def goodreads_from_id(id):
    return goodreads_from(ebook_goodreads_response(id, 'id'))
