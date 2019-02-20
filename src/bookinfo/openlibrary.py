import requests
import json
from joblib import Memory
from config import AppState
# https://openlibrary.org/api/books?bibkeys=ISBN:0201558025&format=json&jscmd=data

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())

@memory.cache()
def ebook_openlibrary_response(isbn):
    url = config['openlibrary']['data_url'].as_str().format(isbn)
    return requests.get(url)

def openlibrary_from_isbn(isbn):
    openlibrary_response = ebook_openlibrary_response(isbn)
    if openlibrary_response.ok:
        openlibrary = json.loads(openlibrary_response.content.decode("utf-8"))
        for value in openlibrary.values():
            return value
