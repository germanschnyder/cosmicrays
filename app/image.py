from pyfits.header import Header
from numpy.core import ndarray


class Image(object):
    def __get_header(self, name):
        return self.__primary_headers.get(name)

    @property
    def bitpix(self):
        return self.__get_header('BITPIX')

    @property
    def target_name(self):
        return self.__get_header('TARGNAME')

    @property
    def is_dark(self):
        return self.target_name == 'DARK'

    @property
    def charge_inject(self):
        return self.__get_header('CHINJECT')

    @property
    def flash_current(self):
        return self.__get_header('FLASHCUR')

    @property
    def file_type(self):
        return self.__get_header('FILETYPE')

    @property
    def data(self):
        return self.__data

    @property
    def extension_info(self):
        return [(ext.get("XTENSION"), ext.get("EXTNAME"), ext.get("EXTVER")) for ext in self.__extensions]

    def extension(self, type, name, version) -> Header:
        return next((ext for ext in self.__extensions
                     if ext.get("XTENSION") == type and
                     ext.get("EXTNAME") == name and
                     int(ext.get("EXTVER")) == version), None)

    def __init__(self, data: ndarray, headers):
        self.__data = data
        self.__primary_headers = headers[0]
        if len(headers) > 1:
            self.__extensions = headers[1:]
