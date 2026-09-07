"""Standardized application context keys shared across DeskMind pages and Brain."""

ACTIVE_NOTE = "active_note"
ACTIVE_PDF = "active_pdf"
SEARCH_DIRECTORY = "search_directory"

KNOWN_KEYS = (ACTIVE_NOTE, ACTIVE_PDF, SEARCH_DIRECTORY)


class AppContext:
    """Thin wrapper around the shared context dictionary.

    All pages and the Brain read and write the same three keys:
    active_note, active_pdf, search_directory.  Using a wrapper keeps
    the key names in one place and prevents typos.
    """

    def __init__(self, data=None):
        self._data = data if data is not None else {}

    @property
    def data(self):
        return self._data

    # active_note --------------------------------------------------

    @property
    def active_note(self):
        return self._data.get(ACTIVE_NOTE)

    @active_note.setter
    def active_note(self, value):
        self._data[ACTIVE_NOTE] = value

    def clear_active_note(self):
        self._data.pop(ACTIVE_NOTE, None)

    # active_pdf ---------------------------------------------------

    @property
    def active_pdf(self):
        return self._data.get(ACTIVE_PDF)

    @active_pdf.setter
    def active_pdf(self, value):
        self._data[ACTIVE_PDF] = value

    def clear_active_pdf(self):
        self._data.pop(ACTIVE_PDF, None)

    # search_directory --------------------------------------------

    @property
    def search_directory(self):
        return self._data.get(SEARCH_DIRECTORY)

    @search_directory.setter
    def search_directory(self, value):
        self._data[SEARCH_DIRECTORY] = value

    def clear_search_directory(self):
        self._data.pop(SEARCH_DIRECTORY, None)

    # general ------------------------------------------------------

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __contains__(self, key):
        return key in self._data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def pop(self, key, default=None):
        return self._data.pop(key, default)
