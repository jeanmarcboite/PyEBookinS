from src.bookinfo.goodreads import goodreads_from_isbn
from src.config import Config
from joblib import Memory
from isbnlib import isbn_from_words as _isbn_from_words, cover
import urllib

memory = Memory(Config.cache.directory, verbose = Config.cache.verbose)
# en, es, af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he, hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl, pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
@memory.cache()
def isbn_from_words(words):
    return _isbn_from_words(words)
# ol covers: http://covers.openlibrary.org/b/$key/$value-$size.jpg

@memory.cache()
def isbn_cover(isbn, provider = 'OpenLibrary'):
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
