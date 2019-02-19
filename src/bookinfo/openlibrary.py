from src.config import Config
import requests
import json
import xml.etree.ElementTree as ElementTree
from joblib import Memory
from config import AppState
# https://openlibrary.org/api/books?bibkeys=ISBN:0201558025&format=json&jscmd=data

config = AppState().config
memory = Memory(config['cache']['directory'].as_filename(),
                verbose=config['cache']['verbose'].get())

@memory.cache()
def ebook_openlibrary_response(isbn):
    return requests.get(Config.openlibrary.data_url.format(isbn))

def openlibrary_from_isbn(isbn):
    openlibrary_response = ebook_openlibrary_response(isbn)
    if openlibrary_response.ok:
        return json.loads(openlibrary_response.content.decode("utf-8"))
