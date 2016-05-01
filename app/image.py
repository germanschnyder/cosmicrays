from pyfits.header import Header
from numpy.core import ndarray


class Image(object):

    def __get_header(self, name):
        return self.__headers.get(name)

    @property
    def extension(self):
        return self.__get_header('XTENSION')

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

    def __init__(self, data: ndarray, headers: Header):
        self.__data = data
        self.__headers = headers
