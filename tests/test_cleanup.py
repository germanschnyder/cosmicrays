import unittest
import os, os.path, sys
from app import cleanup

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCleanupMethods(unittest.TestCase):

    def test_parse(self):
        filename = 'test_raw.fits'

        # only try to open file if it exists
        if os.path.isfile(filename):
            data, hdr = cleanup.load(filename)

            assert data.ndim == 2
            
            assert hdr.get('XTENSION') == 'IMAGE'
            assert hdr.get('BITPIX') == 16


if __name__ == '__main__':
    unittest.main()
