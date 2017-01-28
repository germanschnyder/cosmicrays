import unittest
import os, os.path, sys
import math

from lib import calc_pos

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCalcPosMethods(unittest.TestCase):

    def test_calc_pos(self):
        raw_file_path = os.path.join(os.path.dirname(__file__), 'images/j6mf16lhq_raw.fits')
        spt_file_path = os.path.join(os.path.dirname(__file__), 'images/j6mf16lhq_spt.fits')

        lon, lat, height = calc_pos.calc_pos(spt_file_path, raw_file_path)

        assert math.isclose(lon, -57.96487609991613), "Longitude is %r" % lon
        assert math.isclose(lat, 25.709904336670753), "Latitude is %r" % lat
        assert math.isclose(height, 575.80171745717143), "Height is %r" % height


if __name__ == '__main__':
    unittest.main()
