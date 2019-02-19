from config import AppState

if __name__ == '__main__':
    state = AppState()
    print(state.config.keys())
    print(state.config['library'].as_filename())
    print(state.config['application_name'])
    print(state.config['calibre_db'].as_filename())
    print(state.config['ebook_extensions'])
    print(state.config['goodreads']['url'])
    print(state.config['autre_ancre'])