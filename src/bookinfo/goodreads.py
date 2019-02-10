from src.config import Config
import requests
import xml.etree.ElementTree as ElementTree
from joblib import Memory

memory = Memory(Config.cache.directory, verbose=Config.cache.verbose)

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
def ebook_goodreads_response(isbn):
    url = Config.goodreads.url.format(isbn, Config.goodreads.key)
    return requests.get(url)

@memory.cache()
def goodreads_from_isbn(isbn):
    goodreads_response = ebook_goodreads_response(isbn)
    if goodreads_response.ok:
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

@memory.cache()
def goodreads_from_file(filename):
    return goodreads_from_isbn(isbn_from_file(filename))
