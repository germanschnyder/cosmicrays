import unittest
import os, os.path, sys

from common.instruments import InstrumentUtils
from lib import calc_pos, crutils
from tests import utils

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCalcPosMethods(unittest.TestCase):

    test_images = utils.test_images

    def test_calc_pos(self):

        for instr, filename in self.test_images.items():

            if os.path.isfile(filename):
                ins = InstrumentUtils.instrument_from_name(instr)
                pos_filename = filename.replace(ins.DATA_FILE_EXT[0], ins.POS_FILE_EXT)
                img = crutils.load(filename, pos_filename)

                print("Loaded %s, sending %s" % (filename, pos_filename))
                lon, lat, height = calc_pos.calc_pos(img)

                assert lon is not None, "Longitude is %r" % lon
                assert lat is not None, "Latitude is %r" % lat
                assert height is not None, "Height is %r" % height

                # assert math.isclose(lon, -57.96487609991613), "Longitude is %r" % lon
                # assert math.isclose(lat, 25.709904336670753), "Latitude is %r" % lat
                # assert math.isclose(height, 575.80171745717143), "Height is %r" % height

            else:
                assert False, "Couldn't open %s" % filename


if __name__ == '__main__':
    unittest.main()
