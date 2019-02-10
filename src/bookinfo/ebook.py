from src.bookinfo.isbn import isbn_from_words
from src.config import Config
from ebooklib import epub
from joblib import Memory

memory = Memory(Config.cache.directory, verbose=Config.cache.verbose)


def get_str(item):
    if isinstance(item, (list, tuple)):
        if len(item) == 0:
            return None
        else:
            return get_str(item[0])

    assert isinstance(item, str)
    return item


@memory.cache()
def epub_info(path):
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

    info = dict()
    if 'identifier' in metadata['DC'].keys():
        info['identifier'] = metadata['DC']['identifier']

    for key in ['author', 'description', 'title', 'source']:
        if key in metadata['DC']:
            info[key] = get_str(metadata['DC'][key])

    for (to_key, from_key) in {
        'creation_date': 'date',
        'author': 'creator',
        'language_in_epub': 'language',
        'ISBN': 'source'}.items():
        info[to_key] = get_str(metadata['DC'][from_key])

    info['isbn'] = isbn_from_words(info['author'] + ' ' + info['title'])

    return info
