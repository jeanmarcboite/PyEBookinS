import logging

import requests
import json
from joblib import Memory
from config import AppState
# https://openlibrary.org/api/books?bibkeys=ISBN:0201558025&format=json&jscmd=data
from src.bookinfo.isbn import isbn_from_words

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())
logger = logging.getLogger('bookinfo')

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


@memory.cache()
def openlibrary_from_info(info):
    openlibrary = openlibrary_from_isbn(info.ISBN)
    if openlibrary:
        return openlibrary
    logger.info('{}, no openlibrary entry for {}'.format(info.title, info.ISBN))
    author = ', '.join(list(reversed(info.author.split())))
    isbn = isbn_from_words('{} {}'.format(author, info.title))
    if isbn != info.ISBN:
        logger.info('{}, try again with {}'.format(info.title, info.ISBN))
        info.ISBN = isbn
        openlibrary = openlibrary_from_isbn(info.ISBN)
    if openlibrary:
        return openlibrary
    openlibrary = openlibrary_from_words('{} {}'.format(info.author, info.title))
    language = config['language_code'][info.language[0]].get()
    title = info.title.replace('.', "")
    if openlibrary["num_found"] > 0:
        for doc in openlibrary["docs"]:
            try:
                if doc['title'].replace('.', "") == title and doc["language"][0] == language:
                    doc["identifiers"] = {}
                    doc["identifiers"]["openlibrary"] = doc["key"]
                    doc["identifiers"]["goodreads"] = doc["id_goodreads"]
                    try:
                        doc["identifiers"]["librarything"] = doc['id_librarything']
                    except KeyError:
                        pass
                    return doc

            except KeyError:
                pass


