from app.image import Image
from numpy.core import array
from pyfits import Header
import pyfits


def load(filepath):
    """

    :param filepath: fits image path
    :return: a tuple containing image data and header
    """
    data = pyfits.getdata(filepath, hdu=0)
    primary = Header(pyfits.getheader(filepath, 0))
    headers = [primary]
    extcount = int(primary.get("NEXTEND", 0))
    for idx in range(1, extcount):
        ext = Header(pyfits.getheader(filepath, idx))
        headers.append(ext)
    return Image(array(data), headers)
