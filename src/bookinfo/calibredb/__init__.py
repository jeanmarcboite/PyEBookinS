import logging
from pprint import pprint, pformat

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import AppState
from .tables import Author, Book
from ..isbn import isbn_from_words
config = AppState().config
logger = logging.getLogger('bookinfo')

def get_books(db_uri):
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    books = session.query(Book).all()

    return books


def get_authors(db_uri):
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session.query(Author).all()

    return books

class CalibreDB(dict):
    def __init__(self, database, **kwargs):
        super(CalibreDB, self).__init__(**kwargs)
        self.key = 'isbn'
        self.database = database
        logger.info("Reading calibre database '%s'", self.database)
        for book in get_books(self.database):
            isbn = ''
            try:
                isbn = book.isbn
            except:
                pass

            if len(isbn) < 10:
                isbn = isbn_from_words('{} {}'.format(book.author_sort, book.title))

            if isbn:
                self[isbn] = book
            else:
                self[book.title] = book

    def __repr__(self):
        return pformat(self.__dict__, indent=4)
