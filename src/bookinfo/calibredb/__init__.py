from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .tables import Author, Book

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
