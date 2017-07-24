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

    def __get_header(self, name, sci=False):
        h = self.__primary_headers.get(name)
        if sci or (h is None and self.has_extensions):
            sci_1_ext = self.extension(ImageExtension("SCI", "IMAGE", 1))
            h = sci_1_ext.get(name)
        return h

    def __get_pos(self, name):
        h = self.__pos_headers.get(name)
        if h is None:
            h = self.__get_header(name)
        return h

    @property
    def moon_angle(self)->str:
        return self.__get_header('MOONANGL')

    @property
    def sun_angle(self)->str:
        return self.__get_header('SUNANGLE')

    @property
    def sun_altitude(self)->str:
        return self.__get_header('SUN_ALT')

    @property
    def right_ascension_target(self)->str:
        return self.__get_header('RA_TARG')

    @property
    def declination_target(self)->str:
        return self.__get_header('DEC_TARG')

    @property
    def equinox(self)->str:
        return self.__get_header('EQUINOX')

    @property
    def gain(self) -> str:
        gain = self.__get_header('CCDGAIN')
        if gain is None:
            gain = self.__get_header('ATODGAIN')

        if gain is None:
            gain = self.__get_header('ADCGAIN')
        return gain

    # Already applied maybe ?
    # CCDGAIN
    # CCDAMP (list of amps), then CCDOFST<amp>
    #
    # Only in RAW
    # BSCALE
    # BZERO

    # start wcs attributes

    @property
    def wcs_axes(self)->int:
        return int(self.__get_header('WCSAXES'))

    def wcs_crpix(self, idx: int)->str:
        return self.__get_header('CRPIX{}'.format(idx))

    def wcs_crval(self, idx: int)->str:
        return self.__get_header('CRVAL{}'.format(idx))

    def wcs_ctype(self, idx: int)->str:
        return self.__get_header('CTYPE{}'.format(idx))

    def wcs_cd(self, idx: int, pos: int)->str:
        return self.__get_header('CD{}_{}'.format(idx, pos))

    def wcs_ltv(self, idx: int)->str:
        return self.__get_header('LTV{}'.format(idx))

    def wcs_ltm(self, idx: int)->str:
        return self.__get_header('LTM{}_{}'.format(idx, idx))

    @property
    def wcs_pa_aper(self)->str:
        return self.__get_header('PA_APER')

    @property
    def wcs_va_factor(self)->str:
        return self.__get_header('VAFACTOR')

    @property
    def wcs_orientation(self)->str:
        return self.__get_header('ORIENTAT')

    @property
    def wcs_ra_aperture(self)->str:
        return self.__get_header('RA_APER')

    @property
    def wcs_dec_aperture(self)->str:
        return self.__get_header('DEC_APER')

    # end wcs

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
    def naxis(self)->int:
        return int(self.__get_header('NAXIS', True))

    def naxis_i(self, idx: int)->str:
        return self.__get_header('NAXIS{}'.format(idx))

    @property
    def binaxis1(self)->str:
        return self.__get_header('BINAXIS1')

    @property
    def binaxis2(self)->str:
        return self.__get_header('BINAXIS2')

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
    def bias_correction(self)->str:
        return self.__get_header('BIASCORR')

    @property
    def has_bias_correction(self)->bool:
        return self.bias_correction == 'COMPLETE'

    @property
    def blev_correction(self)->str:
        return self.__get_header('BLEVCORR')

    @property
    def has_blev_correction(self)->bool:
        return self.blev_correction == 'COMPLETE'

    @property
    def cr_mask(self)->str:
        return self.__get_header('CRMASK')

    @property
    def has_cr_mask_applied(self)->bool:
        return self.cr_mask == 'COMPLETE'

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

