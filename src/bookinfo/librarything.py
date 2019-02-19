import requests
from joblib import Memory
from config import AppState

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())

@memory.cache()
def ebook_librarything_response(isbn):
    url = config['librarything']['getwork'].as_str().format(isbn,
                                                            config['librarything']['key'].as_str())
    print(url)
    return requests.get(url)

def librarything_from_isbn(isbn):
    librarything_response = ebook_librarything_response(isbn)
    if librarything_response.ok:
        return librarything_response.content
