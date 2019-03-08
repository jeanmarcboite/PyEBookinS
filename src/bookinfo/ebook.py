import logging
import os
import urllib
from pprint import pformat

import requests
from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT
from joblib import Memory
from langdetect import detect

from config import AppState
from src.bookinfo.goodreads import goodreads_from_id, goodreads_from_isbn
from src.bookinfo.isbn import isbn_from_words, isbn_cover
from src.bookinfo.librarything import librarything_from_id, \
    librarything_from_isbn, librarything_cover
from src.bookinfo.openlibrary import openlibrary_from_info

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())


def _detect_language(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    if len(text) < 100:
        return ''
    return detect(soup.get_text())


def get_str(item):
    if item is None:
        return None
    if isinstance(item, (list, tuple)):
        if len(item) == 0:
            return None
        else:
            return get_str(item[0])

    if not isinstance(item, str):
        print(type(item))
    assert isinstance(item, str)
    return item


def get_identifiers(book):
    identifiers = {}
    dc_identifiers = book.get_metadata('DC', 'identifier')
    for identifier in dc_identifiers:
        if (isinstance(identifier, tuple)
                and isinstance(identifier[0], str)
                and isinstance(identifier[1], dict)):
            for key in identifier[1].values():
                identifiers[key] = identifier[0]
    return identifiers


def get_language(book):
    documents = list(map(lambda item: item.get_body_content(),
                         list(book.get_items_of_type(ITEM_DOCUMENT))))
    return [lang for lang in set(map(_detect_language, documents)) if len(lang) > 0]


@memory.cache()
def book_info(filename, **kwargs):
    info = {}
    logger = logging.getLogger('bookinfo')
    fields = {
        'DC': ['language', 'title', 'creator', 'source', 'subject',
               'contributor', 'publisher', 'rights', 'coverage', 'date', 'description']
    }

    try:
        book = epub.read_epub(filename)
    except (AttributeError, KeyError) as ake:
        logger.error('reading {}'.format(filename))
        logger.error(ake)
        return info

    metadata = {}

    for namespace in fields.keys():
        metadata[namespace] = {}
        for name in fields[namespace]:
            metadata[namespace][name] = book.get_metadata(namespace, name)

    info['identifiers'] = get_identifiers(book)

    for name in ['author', 'description', 'title', 'source', 'cover_image']:
        if name in metadata['DC']:
            info[name] = get_str(metadata['DC'][name])

    for (to_name, from_name) in {
        'creation_date': 'date',
        'author': 'creator',
        'language_in_epub': 'language'}.items():
        if from_name in metadata['DC']:
            info[to_name] = get_str(metadata['DC'][from_name])

    # LANGUAGE
    documents = list(map(lambda item: item.get_body_content(),
                         list(book.get_items_of_type(ITEM_DOCUMENT))))
    info['language'] = [lang for lang in set(map(_detect_language, documents)) if len(lang) > 0]

    # AUTHOR
    try:
        if info['author'].isupper() and len(info['author'].split()) == 2:
            info['author'] = ' '.join(list(map(lambda s: s.strip().capitalize(),
                                               reversed(info['author'].split(',')))))
    except AttributeError:
        pass

    # ISBN
    try:
        info['ISBN'] = info['identifiers']['ISBN']
    except KeyError:
        author = ''
        if info['author'] is not None:
            author = ', '.join(list(reversed(info['author'].split())))

        info['ISBN'] = isbn_from_words('{} {}'.format(author, info['title']))
        logger.info('{}, no isbn in epub, found {} from google'.format(info['title'], info['ISBN']))

    # OPENLIBRARY
    info['openlibrary'] = openlibrary_from_info(info['author'], info['title'],
                                                info['language'], info['ISBN'])
    if not info['openlibrary']:
        del info['openlibrary']
    else:
        try:
            info['ISBN'] = info['openlibrary']['ISBN']
        except KeyError:
            pass

    # GOODREADS, LIBRARYTHING
    for k, f in {'goodreads': (goodreads_from_id, goodreads_from_isbn),
                 'librarything': (librarything_from_id, librarything_from_isbn)}.items():
        try:
            info[k] = f[0](info['openlibrary']['identifiers'][k][0])
        except (AttributeError, KeyError):
            info[k] = f[1](info['ISBN'])

    try:
        if info['description'] is None:
            info['description'] = info['goodreads']['book']['description']
    except KeyError:
        pass

    return info

@memory.cache()
def curl(url):
    return urllib.request.urlopen(url).read()

class BookInfo():
    logger = logging.getLogger('bookinfo')

    def __init__(self, filename, **kwargs):
        super(BookInfo, self).__init__(**kwargs)
        self.filename = filename

        for k, v in book_info(filename).items():
            self.__setattr__(k, v)

        cover = os.path.join(os.path.dirname(filename), 'cover.jpg')
        if os.path.isfile(cover):
            self.cover_image = open(cover, 'rb').read()
        self.get_cover()
        # fix author name, goodreads usually better
        try:
            self.author = self.goodreads['book/authors/author']['name']
        except (AttributeError, KeyError):
            pass

        # if calibre_db:
        # info['calibre'] = calibre_db[info['isbn']]

    def get_cover(self):

        try:
            self.cover_image
            return
        except AttributeError:
            pass

        try:
            cover_image = curl(self.openlibrary['cover']['large'])
            if len(cover_image) > 1000:
                self.cover_image = cover_image
                return
        except (KeyError, AttributeError):
            pass

        try:

            cover_image = librarything_cover(self.librarything['url'])
            if len(cover_image) > 1000:
                self.cover_image = cover_image
                return
        except (KeyError, AttributeError):
            pass

        try:
            cover_image = isbn_cover(self.ISBN, 'librarything')
            if len(cover_image) > 1000:
                self.cover_image = cover_image
                return

        except AttributeError:
            pass
        try:
            self.image_url = self.goodreads['book']['image_url']
            return
        except (AttributeError, KeyError):
            pass
        try:
            self.image_url = config['openlibrary']['cover_url'].as_str().format(self.openlibrary['cover_edition_key'])
            return
        except (TypeError, AttributeError, KeyError):
            pass
        try:
            self.cover_image
            return
        except AttributeError:
            try:
                self.cover_image = isbn_cover(self.ISBN, 'goodreads')
            except AttributeError:
                pass

    def __repr__(self):
        d = self.__dict__.copy()
        try:
            del d['cover_image']
        except:
            pass
        return pformat(d)
