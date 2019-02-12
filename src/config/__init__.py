import os


class ConfigItem(object):
    def __init__(self):
        pass


class Config:
    project_directory = os.path.realpath('..')
    application_name = 'BookinS'
    cache = ConfigItem()
    cache.directory = '~/.cache'
    cache.verbose = 1
    book_extensions = ['epub']

    goodreads = ConfigItem()
    goodreads.key = 'iKEG2vmZFhfw1GkHkMRk7w'
    goodreads.url = "https://www.goodreads.com/book/isbn/{}?key={}"

    openlibrary = ConfigItem()
    openlibrary.cover_url = 'http://covers.openlibrary.org/b/ISBN/{}-L.jpg'
    openlibrary.data_url = "https://openlibrary.org/api/books?bibkeys=ISBN:{}&format=json&jscmd=data"

if __name__ == '__main__':
    x = Config.cache
    x.z = 'z'
    print(x.z)
    print(x.directory)
    x.directory = 'Z'
    print(Config.cache.directory)
