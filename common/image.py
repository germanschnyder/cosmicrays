from astropy.io.fits.header import Header
from numpy.core import ndarray

from common.instruments import InstrumentUtils, Instrument


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
        h = self.__primary_headers.get(name)
        if h is None and self.has_extensions:
            sci_1_ext = self.extension(ImageExtension("SCI", "IMAGE", 1))
            h = sci_1_ext.get(name)
        return h

    def __get_pos(self, name):
        h = self.__pos_headers.get(name)
        if h is None:
            h = self.__get_header(name)
        return h

    @property
    def aperture(self)->str:
        return self.__get_pos('APER_REF')

    @property
    def ecliptic_lon(self)->str:
        return self.__get_pos('ELON_REF')

    @property
    def ecliptic_lat(self)->str:
        return self.__get_pos('ELAT_REF')

    @property
    def galactic_lon(self)->str:
        return self.__get_pos('GLON_REF')

    @property
    def galactic_lat(self)->str:
        return self.__get_pos('GLAT_REF')

    @property
    def postnstx(self)->str:
        return self.__get_pos('POSTNSTX')

    @property
    def postnsty(self)->str:
        return self.__get_pos('POSTNSTY')

    @property
    def postnstz(self)->str:
        return self.__get_pos('POSTNSTZ')

    @property
    def bitpix(self)->str:
        return self.__get_header('BITPIX')

    @property
    def proposal_id(self)->str:
        return self.__get_header('PROPOSID')

    @property
    def target_name(self)->str:
        return self.__get_header('TARGNAME')

    @property
    def position_angle(self)->str:
        return self.__get_pos('PA_V3')

    @property
    def right_ascension(self)->str:
        return self.__get_pos('RA_V1')

    @property
    def declination(self)->str:
        return self.__get_pos('DEC_V1')

    @property
    def is_dark(self)->bool:
        return self.target_name == 'DARK'

    @property
    def cr_rejected_perform(self)->str:
        return self.__get_header('CRCORR')

    @property
    def has_cr(self)->bool:
        return self.cr_rejected_perform == 'OMIT'

    @property
    def has_extensions(self)->bool:
        return len(self.__extensions) > 0

    @property
    def charge_inject(self)->str:
        return self.__get_header('CHINJECT')

    @property
    def flash_current(self)->str:
        return self.__get_header('FLASHCUR')

    @property
    def file_name(self)->str:
        return self.__get_header('FILENAME')

    @property
    def observation_set(self)->str:
        return self.__get_header('ROOTNAME')

    @property
    def file_type(self)->str:
        return self.__get_header('FILETYPE')

    @property
    def instrument(self) -> Instrument:
        return InstrumentUtils.instrument_from_name(self.__get_header('INSTRUME'))

    @property
    def exposition_duration(self)->str:
        return self.__get_header('EXPTIME')

    @property
    def observation_date(self)->str:
        return self.__get_header('DATE-OBS')

    @property
    def observation_start_time(self)->str:
        return self.__get_header('TIME-OBS')

    @property
    def data(self)->ndarray:
        return self.__data

    @property
    def extension_info(self):
        return [ImageExtension(ext.get("XTENSION"), ext.get("EXTNAME"), ext.get("EXTVER")) for ext in self.__extensions]

    def extension(self, info: ImageExtension) -> Header:
        return next((ext for ext in self.__extensions
                     if ext.get("XTENSION") == info.type and
                     ext.get("EXTNAME") == info.name and
                     int(ext.get("EXTVER")) == info.version), None)

    def __init__(self, data: ndarray, headers: [Header], pos: [Header]):
        assert headers is not None, "You must specify at least primary headers"
        assert len(headers) > 0, "You must specify at least primary headers"
        self.__data = data
        self.__pos_headers = pos[0]
        self.__primary_headers = headers[0]
        if len(headers) > 1:
            self.__extensions = headers[1:]
        else:
            self.__extensions = []

