import unittest
import os, os.path, sys

from lib import calc_pos

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCalcPosMethods(unittest.TestCase):

    def test_calc_pos(self):
        raw_file_path = os.path.join(os.path.dirname(__file__), 'test_raw.fits')
        spt_file_path = os.path.join(os.path.dirname(__file__), 'test_spt.fits')

        lon, lat, height = calc_pos.calc_pos(spt_file_path, raw_file_path)

        assert lon == 177.60277060584357, "Longitude is %r" % lon
        assert lat == -19.234216331408884, "Latitude is %r" % lat
        assert height == 564.6053939531912, "Height is %r" % height


if __name__ == '__main__':
    unittest.main()
