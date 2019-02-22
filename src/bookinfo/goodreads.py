import requests
import xml.etree.ElementTree as ElementTree
from joblib import Memory
from config import AppState
from bs4 import BeautifulSoup

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())

# https://www.goodreads.com/book/show/50.xml?key=iKEG2vmZFhfw1GkHkMRk7w
class Goodreads():
    attributes = {
        'book': [
            'id', 'title',
            'description',
            'image_url',
            'language_code',
            'isbn',
            'average_rating','ratings_count',
            'link',
            'num_pages'
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
            'id', 'name', 'image_url', 'link',
            'average_rating','ratings_count',
        ]
    }

@memory.cache()
def ebook_goodreads_request(url):
    return requests.get(url, allow_redirects=False)
@memory.cache()
def ebook_goodreads_response(goodreads_id, id_type='id'):
    url = config['goodreads']['url'][id_type].as_str().format(goodreads_id,
                                                config['goodreads']['key'].get())
    response = ebook_goodreads_request(url)
    if response.ok:
        # if we get html, we are redirected
        if response.headers['Content-Type'].strip() == 'text/html; charset=utf-8':
            soup = BeautifulSoup(response.content, 'html.parser')
            tag = soup.find('a')
            s = str(tag)
            g_id = s.split('book/show/')[1].split('.')[0]
            return ebook_goodreads_response(g_id)
    return response
def goodreads_from(goodreads_response):
    if goodreads_response.ok:
        with open('/home/box/tmp/goodreads', 'w') as output_file:
            output_file.write(goodreads_response.content.decode("utf-8") )
        root = ElementTree.fromstring(goodreads_response.content.decode("utf-8"))
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
