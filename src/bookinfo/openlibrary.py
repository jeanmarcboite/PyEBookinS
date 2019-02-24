import logging

import confuse
import requests
import json
from copy import copy
from joblib import Memory
from config import AppState
# https://openlibrary.org/api/books?bibkeys=ISBN:0201558025&format=json&jscmd=data
from src.bookinfo.isbn import isbn_from_words

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())
logger = logging.getLogger('bookinfo')


class Openlibrary(dict):
    def __init__(self, doc):
        super(Openlibrary, self).__init__()
        if doc and isinstance(doc, dict):
            for k, v in doc.items():
                self[k] = copy(v)
            self.url = config['openlibrary']['url'].as_str().format(self['key'])

@memory.cache()
def ebook_openlibrary_response(isbn):
    url = config['openlibrary']['data_url'].as_str().format(isbn)
    return requests.get(url)

def openlibrary_from_isbn(isbn):
    openlibrary_response = ebook_openlibrary_response(isbn)
    if openlibrary_response.ok:
        openlibrary = json.loads(openlibrary_response.content.decode("utf-8"))
        for value in openlibrary.values():
            return value


#  https://openlibrary.org/search.json?q=Woolf+Virginia+Mrs+Dalloway
# "_".join( title.split() )
@memory.cache()
def openlibrary_from_words(words):
    url = 'https://openlibrary.org/search.json?q={}'.format('+'.join(words.split()))
    response = requests.get(url)
    if response.ok:
        return json.loads(response.content.decode('utf-8'))
    return None


def openlibrary_from_info(info):
    logger.info('{},  {}'.format(info.title, info.ISBN))
    openlibrary = openlibrary_from_isbn(info.ISBN)
    if openlibrary:
        return Openlibrary(openlibrary)
    logger.info('{}, no openlibrary entry for {}'.format(info.title, info.ISBN))
    author = ', '.join(list(reversed(info.author.split())))
    isbn = isbn_from_words('{} {}'.format(author, info.title))
    if isbn != info.ISBN:
        logger.info('{}, try again with {}'.format(info.title, info.ISBN))
        info.ISBN = isbn
        openlibrary = openlibrary_from_isbn(info.ISBN)
    if openlibrary:
        return Openlibrary(openlibrary)
    openlibrary = openlibrary_from_words('{} {}'.format(info.author, info.title))
    try:
        language = config['language_code'][info.language[0]].get()
    except confuse.ConfigError as ce:
        logger.error(str(ce))
        language = info.language[0]
    title = info.title.replace('.', "")
    if openlibrary["num_found"] > 0:
        for doc in openlibrary["docs"]:
            try:
                if doc['title'].replace('.', "") == title and doc["language"][0] == language:
                    doc["identifiers"] = {}
                    for (k, v) in {
                        "openlibrary": "key",
                        "goodreads": "id_goodreads",
                        "librarything": "id_librarything"
                    }.items():
                        try:
                            doc['identifiers'][k] = doc[v]
                        except KeyError:
                            pass
                    return Openlibrary(doc)
            except KeyError:
                pass
    return None

