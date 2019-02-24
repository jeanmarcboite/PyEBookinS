import logging

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
        print("+Reading calibre database '{}'".format(self.database))
        logger.setLevel(10)
        logger.info("Reading calibre database '%s'", self.database)
        print(logger.getEffectiveLevel(

        ))
        for book in get_books(self.database):
            isbn = ''
            try:
                isbn = book.isbn
            except:
                pass

            if len(isbn) < 10:
                isbn = isbn_from_words('{} {}'.format(book.author_sort, book.title))

            self[isbn] = book
