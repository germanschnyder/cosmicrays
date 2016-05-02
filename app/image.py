from pyfits.header import Header
from numpy.core import ndarray


class ImageExtension(object):

    @property
    def name(self):
        return self.__name

    @property
    def version(self):
        return self.__version

    @property
    def type(self):
        return self.__type

    def __init__(self, name: str, type: str, version: int):
        self.__name = name
        self.__type = type
        self.__version = version


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
        return [ImageExtension(ext.get("XTENSION"), ext.get("EXTNAME"), ext.get("EXTVER")) for ext in self.__extensions]

    def extension(self, info: ImageExtension) -> Header:
        return next((ext for ext in self.__extensions
                     if ext.get("XTENSION") == info.type and
                     ext.get("EXTNAME") == info.name and
                     int(ext.get("EXTVER")) == info.version), None)

    def __init__(self, data: ndarray, headers):
        assert headers is not None, "You must specify at least primary headers"
        assert len(headers) > 0, "You must specify at least primary headers"
        self.__data = data
        self.__primary_headers = headers[0]
        if len(headers) > 1:
            self.__extensions = headers[1:]
