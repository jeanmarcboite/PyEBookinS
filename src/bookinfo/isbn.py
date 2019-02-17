import time
import urllib

from isbnlib import isbn_from_words as _isbn_from_words, cover
from joblib import Memory

from src.bookinfo.goodreads import goodreads_from_isbn
from src.config import Config

isbn_cache = {}
memory = Memory(Config.cache.directory, verbose=Config.cache.verbose)
# en, es, af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he, hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl, pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw

import os, os.path
import json


def isbn_from_words(words):
    global isbn_cache
    if not isbn_cache:
        if Config.cache.isbn:
            if os.path.isfile(Config.cache.isbn):
                with open(Config.cache.isbn) as json_file:
                    isbn_cache = json.load(json_file)
    try:
        isbn = isbn_cache[words]
    except:
        isbn = None
        while isbn is None:
            try:
                isbn = _isbn_from_words(words)
            except ConnectionResetError:
                time.sleep(1)
        isbn_cache[words] = isbn

        if not os.path.exists(os.path.dirname(Config.cache.isbn)):
            os.makedirs(os.path.dirname(Config.cache.isbn))
        with open(Config.cache.isbn, 'w') as json_file:
            json.dump(isbn_cache, json_file, sort_keys=True, indent=1)
    return isbn


# ol covers: http://covers.openlibrary.org/b/$key/$value-$size.jpg

@memory.cache()
def isbn_cover(isbn, provider='OpenLibrary'):
    url = None
    if provider == 'goodreads':
        try:
            url = goodreads_from_isbn(isbn)['book/image_url']
        except KeyError:
            pass
    if provider == 'google':
        google_cover = cover(isbn)
        if google_cover:
            url = google_cover['thumbnail']
    if url is None:
        url = Config.openlibrary.cover_url.format(isbn)
    if url:
        try:
            return urllib.request.urlopen(url).read()

        except ConnectionResetError:
            pass
    if provider != 'google':
        return isbn_cover(isbn, 'google')
    return None
