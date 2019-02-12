from src.config import Config
import requests
import json
import xml.etree.ElementTree as ElementTree
from joblib import Memory
# https://openlibrary.org/api/books?bibkeys=ISBN:0201558025&format=json&jscmd=data

memory = Memory(Config.cache.directory, verbose=Config.cache.verbose)

@memory.cache()
def ebook_openlibrary_response(isbn):
    return requests.get(Config.openlibrary.data_url.format(isbn))

def openlibrary_from_isbn(isbn):
    openlibrary_response = ebook_openlibrary_response(isbn)
    if openlibrary_response.ok:
        return json.loads(openlibrary_response.content.decode("utf-8"))
