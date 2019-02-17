from bs4 import BeautifulSoup

from src.bookinfo.goodreads import goodreads_from_isbn
from src.bookinfo.isbn import isbn_from_words, isbn_cover
from src.config import Config
from ebooklib import epub, ITEM_DOCUMENT
from joblib import Memory
from langdetect import detect

memory = Memory(Config.cache.directory, verbose=Config.cache.verbose)


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

class BookInfo(dict):
    def __init__(self, filename, **kwargs):
        super(BookInfo, self).__init__(**kwargs)
        self.filename = filename

@memory.cache()
def epub_info(path, calibre_db=None):
    fields = {
        'DC': ['language', 'title', 'creator', 'identifier', 'source', 'subject',
               'contributor', 'publisher', 'rights', 'coverage', 'date', 'description']
    }

    book = epub.read_epub(path)

    metadata = {}
    for namespace in fields.keys():
        metadata[namespace] = {}
        for name in fields[namespace]:
            metadata[namespace][name] = book.get_metadata(namespace, name)

    info = BookInfo(path)
    if 'identifier' in metadata['DC'].keys():
        info['identifier'] = metadata['DC']['identifier']

    for key in ['author', 'description', 'title', 'source', 'cover_image']:
        if key in metadata['DC']:
            info[key] = get_str(metadata['DC'][key])

    for (to_key, from_key) in {
        'creation_date': 'date',
        'author': 'creator',
        'language_in_epub': 'language'}.items():
        info[to_key] = get_str(metadata['DC'][from_key])

    if info['author'].isupper() and len(info['author'].split()) == 2:
        info['author'] = ' '.join(list(map(lambda s: s.strip().capitalize(), reversed(info['author'].split(',')))))

    info['isbn'] = isbn_from_words(info['author'] + ' ' + info['title'])
    info['goodreads'] = goodreads_from_isbn(info['isbn'])
    if 'cover_image' not in info.keys():
        info['cover_image'] = isbn_cover(info['isbn'], 'goodreads')
    documents = list(map(lambda item: item.get_body_content(),
                         list(book.get_items_of_type(ITEM_DOCUMENT))))
    info['language'] = [lang for lang in set(map(_detect_language, documents)) if len(lang) > 0]

    if calibre_db:
        info['calibre'] = calibre_db[info['isbn']]

    return info
