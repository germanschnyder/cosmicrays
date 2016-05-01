from app.image import Image
from . import cosmics
from pyfits import header
from numpy.core import array


def load(filepath):
    """

    :param filepath: fits image path
    :return: a tuple containing image data and headers separately
    """
    data, hdr = cosmics.fromfits(filepath, hdu=0, verbose=False)
    return Image(array(data), header.Header(hdr))
