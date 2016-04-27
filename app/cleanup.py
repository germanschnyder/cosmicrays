from . import cosmics
from pyfits import header
from numpy.core import array


def load(filepath):
    data, hdr = cosmics.fromfits(filepath, hdu=0, verbose=False)
    return array(data), header.Header(hdr)
