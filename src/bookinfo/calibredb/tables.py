from sqlalchemy import Column, Integer, Text, TIMESTAMP, TEXT, BOOLEAN, REAL, BLOB, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    sort = Column(Text)
    link = Column(TEXT, nullable=False)
    books = relationship('Book',
                         secondary='books_authors_link',
                         back_populates='authors')

    def __repr__(self):
        return "<Author(name='{}', sort='{}', link='{}')>".format(
            self.name, self.sort, self.link
        )


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=False, default='Unknown')
    sort = Column(Text)
    timestamp = Column(TIMESTAMP)
    pubdate = Column(TIMESTAMP)
    series_index = Column(REAL)
    authors = relationship("Author",
                           secondary='books_authors_link',
                           back_populates='books')
    author_sort = Column(TEXT)
    publishers = relationship("Publisher",
                              secondary='books_publishers_link',
                              back_populates='books')
    language = relationship("Language",
                            secondary='books_languages_link',
                            back_populates='books')
    comments = relationship("Comments", uselist=False, back_populates="book_")
    rating = relationship("Rating",
                          secondary='books_ratings_link',
                          back_populates='books')
    serie = relationship("Serie",
                         secondary='books_series_link',
                         back_populates='books')
    tags = relationship("Tag",
                        secondary='books_tags_link',
                        back_populates='books')
    isbn = Column(TEXT)
    lccn = Column(TEXT)
    path = Column(TEXT)
    flags = Column(Integer, nullable=False, default=1)
    uuid = Column(TEXT)
    has_cover = Column(BOOLEAN, default=False)
    last_modified = Column(TIMESTAMP, nullable=False, default='2000-01-01 00:00:00+00:00')

    def __repr__(self):
        return """<Book(id={}, title='{}', sort='{}', 
        timestamp='{}', pubdate='{}',
        authors='{}',author_sort='{}',
        publishers='{}',language='{}',
        comments='{}',
        rating='{}',serie='{}[{}]',tags='{}',
        isbn='{}', lccn='{}',
        path='{}',flags='{}',
        uuid='{}', has_cover='{}',
        last_modified=)>""".format(self.id,
            self.title, self.sort,
            self.timestamp, self.pubdate,
            self.authors, self.author_sort,
            self.publishers,self.language,
                                   self.comments,
            self.rating,self.serie,self.series_index,self.tags,
            self.isbn, self.lccn, self.path, self.flags, self.uuid,
            self.has_cover, self.last_modified)


class BooksAuthors(Base):
    __tablename__ = 'books_authors_link'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    author = Column(Integer, ForeignKey('authors.id'), nullable=False)


class BooksCustomColumns2(Base):
    __tablename__ = 'books_custom_column_2_link'

    id = Column(Integer, primary_key=True, autoincrement=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    value = Column(Integer, nullable=False)


class BooksLanguages(Base):
    __tablename__ = 'books_languages_link'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    lang_code = Column(Integer, ForeignKey('languages.id'), nullable=False)
    item_order = Column(Integer, nullable=False)


class BooksPluginData(Base):
    __tablename__ = 'books_plugin_data'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    name = Column(Integer, nullable=False)
    val = Column(Text, nullable=False)


class BooksPublishers(Base):
    __tablename__ = 'books_publishers_link'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    publisher = Column(Integer, ForeignKey('publishers.id'), nullable=False)


class BooksRatings(Base):
    __tablename__ = 'books_ratings_link'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    rating = Column(Integer, ForeignKey('ratings.id'), nullable=False)


class BooksSeries(Base):
    __tablename__ = 'books_series_link'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    series = Column(Integer, ForeignKey('series.id'), nullable=False)


class BookTags(Base):
    __tablename__ = 'books_tags_link'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    tag = Column(Integer, ForeignKey('tags.id'), nullable=False)


class Comments(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'))
    book_ = relationship("Book", back_populates="comments")
    text = Column(TEXT, nullable=False)

    def __repr__(self):
        return self.text


class ConversionOptions(Base):
    __tablename__ = 'conversion_options'

    id = Column(Integer, primary_key=True)
    format = Column(Text, nullable=False)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    data = Column(BLOB, nullable=False)


class CustomColumn2(Base):
    __tablename__ = 'custom_column_2'

    id = Column(Integer, primary_key=True)
    value = Column(Text, nullable=False, unique=True)


class CustomColumn3(Base):
    __tablename__ = 'custom_column_3'

    id = Column(Integer, primary_key=True)
    value = Column(Text, nullable=False, unique=True)


class CustomColumn(Base):
    __tablename__ = 'custom_columns'

    id = Column(Integer, primary_key=True)
    label = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    datatype = Column(Text, nullable=True)
    mark_for_delete = Column(BOOLEAN, default=False)
    editable = Column(BOOLEAN, default=True)
    display = Column(Text, nullable=False, default='{}')
    is_multiple = Column(BOOLEAN, default=False)
    normalized = Column(BOOLEAN)


class Data(Base):
    __tablename__ = 'data'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    format = Column(Text, nullable=False)
    uncompressed_size = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)


class Feed(Base):
    __tablename__ = 'feeds'

    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False, unique=True)
    script = Column(Text, nullable=False)


class Identifier(Base):
    __tablename__ = 'identifiers'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    type = Column(Text, nullable=False, default="isbn")
    val = Column(Text, nullable=False)


class Language(Base):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    lang_code = Column(Text, nullable=False, unique=True)
    books = relationship("Book",
                         secondary='books_languages_link',
                         back_populates='language')

    def __repr__(self):
        return "<Language(lang_code='{}')>".format(
            self.lang_code
        )


class LastReadPositions(Base):
    __tablename__ = 'last_read_positions'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False)
    format = Column(Text, nullable=False)
    user = Column(Text, nullable=False)
    device = Column(Text, nullable=False)
    cfi = Column(Text, nullable=False)
    epoch = Column(REAL, nullable=False)
    pos_frac = Column(REAL, nullable=False, default=0)


class LibraryId(Base):
    __tablename__ = 'library_id'

    id = Column(Integer, primary_key=True)
    uuid = Column(Text, nullable=False, unique=True)


class MetadataDirtied(Base):
    __tablename__ = 'metadata_dirtied'

    id = Column(Integer, primary_key=True)
    book = Column(Integer, ForeignKey('books.id'), nullable=False, unique=True)


class Preferences(Base):
    __tablename__ = 'preferences'

    id = Column(Integer, primary_key=True)
    key = Column(Text, nullable=False, unique=True)
    val = Column(Text, nullable=False)


class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    sort = Column(Text, nullable=False)
    books = relationship('Book',
                         secondary='books_publishers_link',
                         back_populates='publishers')

    def __repr__(self):
        return "<Publisher(name='{}', sort='{}')>".format(
            self.name, self.sort
        )


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable=False)
    books = relationship("Book",
                         secondary='books_ratings_link',
                         back_populates='rating')

    def __repr__(self):
        return "<Rating(rating='{}')>".format(
            self.rating
        )


class Serie(Base):
    __tablename__ = 'series'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    sort = Column(Text)
    books = relationship('Book',
                         secondary='books_series_link',
                         back_populates='serie')

    def __repr__(self):
        return "<Serie(name='{}', sort='{}')>".format(
            self.name, self.sort
        )


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    books = relationship('Book',
                         secondary='books_tags_link',
                         back_populates='tags')

    def __repr__(self):
        return "<Tag(name='{}')>".format(
            self.name
        )

def __repr__(self):
    return "<Tag(name='{}')>".format(
        self.name
    )
