from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, FLOAT, TEXT, BOOLEAN, ForeignKey, Table
from sqlalchemy.orm import relationship

Base = declarative_base()

books_authors_link = Table('books_authors_link',
                           Base.metadata,
                           Column('book', Integer, ForeignKey('books.id')),
                           Column('author', Integer, ForeignKey('authors.id')),
                           )


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False, default='Unknown')
    sort = Column(Text)
    timestamp = Column(TIMESTAMP)
    pubdate = Column(TIMESTAMP)
    series_index = Column(FLOAT)
    authors = relationship("Author",
                           secondary=books_authors_link,
                           back_populates='books')
    author_sort = Column(TEXT)
    lccn = Column(TEXT)
    path  = Column(TEXT)
    flags = Column(TEXT)
    uuid = Column(TEXT)
    has_cover = Column(BOOLEAN, default=False)
    last_modified = Column(TIMESTAMP, nullable=False, default='2000-01-01 00:00:00+00:00')


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    sort = Column(Text)
    link = Column(TEXT, nullable=False)
    books = relationship('Book',
                         secondary=books_authors_link,
                         back_populates='authors')
