from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .tables import Author, Book
from ..isbn import isbn_from_words

db_uri='sqlite:///metadata.db'

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
        for book in get_books(self.database):
            isbn = ''
            try:
                isbn = book.isbn
            except:
                pass

            if len(isbn) < 10:
                isbn = isbn_from_words('{} {}'.format(book.author_sort, book.title))

            self[isbn] = book
