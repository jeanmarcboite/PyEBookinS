from pprint import pformat

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT
from joblib import Memory
from langdetect import detect

from config import AppState
from src.bookinfo.goodreads import goodreads_from_id, goodreads_from_isbn
from src.bookinfo.isbn import isbn_from_words, isbn_cover
from src.bookinfo.librarything import librarything_from_id, librarything_from_isbn
from src.bookinfo.openlibrary import openlibrary_from_isbn, openlibrary_from_words, openlibrary_from_info

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
    if isinstance(item, (list, tuple)):
        if len(item) == 0:
            return None
        else:
            return get_str(item[0])

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


def book_info(filename, calibre_db, **kwargs):
    return BookInfo(filename, calibre_db, **kwargs)


class BookInfo(dict):
    fields = {
        'DC': ['language', 'title', 'creator', 'source', 'subject',
               'contributor', 'publisher', 'rights', 'coverage', 'date', 'description']
    }

    def __init__(self, filename, calibre_db, **kwargs):
        super(BookInfo, self).__init__(**kwargs)
        self.filename = filename

        book = epub.read_epub(self.filename)

        metadata = {}

        for namespace in BookInfo.fields.keys():
            metadata[namespace] = {}
            for name in BookInfo.fields[namespace]:
                metadata[namespace][name] = book.get_metadata(namespace, name)

        self.identifiers = get_identifiers(book)

        for key in ['author', 'description', 'title', 'source', 'cover_image']:
            if key in metadata['DC']:
                setattr(self, key, get_str(metadata['DC'][key]))
        for (to_key, from_key) in {
            'creation_date': 'date',
            'author': 'creator',
            'language_in_epub': 'language'}.items():
            setattr(self, to_key, get_str(metadata['DC'][from_key]))

        try:
            if self.author.isupper() and len(self.author.split()) == 2:
                self.author = ' '.join(list(map(lambda s: s.strip().capitalize(), reversed(self.author.split(',')))))
        except AttributeError:
            pass

        try:
            self.ISBN = self.identifiers['ISBN']
            print('{}, found {} in epub'.format(self.title, self.ISBN))
        except KeyError:
            author = ', '.join(list(reversed(self.author.split())))
            self.ISBN = isbn_from_words('{} {}'.format(author, self.title))
            print('{}, no isbn in epub, found {} from google'.format(self.title, self.ISBN))

        self.language = get_language(book)

        self.openlibrary = openlibrary_from_info(self)

        if self.openlibrary:
            try:
                self.goodreads = goodreads_from_id(self.openlibrary['identifiers']['goodreads'][0])
            except KeyError:
                pass
            try:
                self.librarything = librarything_from_id(self.openlibrary['identifiers']['librarything'][0])
            except KeyError:
                pass
        else:
            self.openlibrary = openlibrary_from_words('{} {}'.format(self.author, self.title))
            print('{}, no openlibrary entry for {} try to get goodreads and librarything from isbn'.format(self.title, self.ISBN))
            self.goodreads = goodreads_from_isbn(self.ISBN)
            self.librarything = librarything_from_isbn(self.ISBN)

        try:
            self.cover_image
        except AttributeError:
            self.cover_image = isbn_cover(self.ISBN, 'goodreads')
        # if calibre_db:
        # info['calibre'] = calibre_db[info['isbn']]

    def __repr__(self):
        return pformat(self.__dict__)
