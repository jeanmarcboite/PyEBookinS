from src.config import Config
import requests
from joblib import Memory

memory = Memory(Config.cache.directory, verbose=Config.cache.verbose)

@memory.cache()
def ebook_librarything_response(isbn):
    url = Config.librarything.getwork.format(isbn, Config.librarything.key)
    print(url)
    return requests.get(url)
@memory.cache()
def librarything_from_isbn(isbn):
    librarything_response = ebook_librarything_response(isbn)
    if librarything_response.ok:
        print(librarything_response.content)
