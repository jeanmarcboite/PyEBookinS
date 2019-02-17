import os


class ConfigItem(object):
    def __init__(self):
        pass


class Config:
    project_directory = os.path.realpath('..')
    application_name = 'BookinS'
    cache = ConfigItem()
    cache.directory = '~/.cache'
    cache.isbn = '/home/box/.cache/isbn/isbn_from_words'
    cache.verbose = 1
    book_extensions = ['epub']

    goodreads = ConfigItem()
    goodreads.key = 'iKEG2vmZFhfw1GkHkMRk7w'
    goodreads.url = "https://www.goodreads.com/book/isbn/{}?key={}"

    openlibrary = ConfigItem()
    openlibrary.cover_url = 'http://covers.openlibrary.org/b/ISBN/{}-L.jpg'
    openlibrary.data_url = "https://openlibrary.org/api/books?bibkeys=ISBN:{}&format=json&jscmd=data"

    librarything = ConfigItem()
    # http: // www.librarything.com / services / rest / 1.1 /?method = librarything.ck.getwork & id = 1060 & apikey = d231aa37c9b4f5d304a60a3d0ad1dad4
    librarything.getwork='http://www.librarything.com/services/rest/1.1/?method=librarything.ck.getwork&isbn={}&apikey={}'
    librarything.key='3a88914e5ef7d402e75bdbdcda333f4f'

if __name__ == '__main__':
    x = Config.cache
    x.z = 'z'
    print(x.z)
    print(x.directory)
    x.directory = 'Z'
    print(Config.cache.directory)
