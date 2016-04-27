import unittest
import os, os.path, sys
from app import cleanup
from pyfits import header

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCleanupMethods(unittest.TestCase):

    def test_parse(self):
        filename = 'test_spt.fits'

        # only try to open file if it exists
        if os.path.isfile(filename):
            data, hdr = cleanup.load(filename)
            imghdr = header.Header(hdr)

            assert imghdr.get('XTENSION') == 'IMAGE'
            assert imghdr.get('BITPIX') == 16

            #print(imghdr)

if __name__ == '__main__':
    unittest.main()
