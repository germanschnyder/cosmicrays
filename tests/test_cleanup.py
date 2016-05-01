import unittest
import os, os.path, sys
from app import cleanup
from app.image import Image

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCleanupMethods(unittest.TestCase):

    def test_parse_raw(self):

        filename = 'test_raw.fits'

        # only try to open file if it exists
        if os.path.isfile(filename):
            img = cleanup.load(filename)

            assert img.extension == 'IMAGE'
            assert img.bitpix == 16
            assert img.charge_inject is None

    def test_parse_spt(self):

        filename = 'test_spt.fits'

        # only try to open file if it exists
        if os.path.isfile(filename):
            img = cleanup.load(filename)

            assert img.charge_inject == 'NONE'

if __name__ == '__main__':
    unittest.main()
