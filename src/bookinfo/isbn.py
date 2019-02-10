from src.config import Config
from joblib import Memory
from isbnlib import  isbn_from_words as _isbn_from_words

memory = Memory(Config.cache.directory, verbose = Config.cache.verbose)

@memory.cache()
def isbn_from_words(words):
    return _isbn_from_words(words)
