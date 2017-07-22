import unittest
import os, os.path, sys

import time

from common.instruments import InstrumentUtils
from lib import calc_pos, crutils, crstats
from tests import utils

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCalcPosMethods(unittest.TestCase):

    test_images = utils.test_images

    def test_pipeline(self):
        for instr, filename in self.test_images.items():

            if os.path.isfile(filename):
                ins = InstrumentUtils.instrument_from_name(instr)
                pos_filename = filename.replace(ins.DATA_FILE_EXT[0], ins.POS_FILE_EXT)
                start = time.time()
                img = crutils.load(filename, pos_filename)
                _, cr_pixels = crutils.clean_cr(img.data, mask=None, iterations=1, gain=img.gain)

                crs, normalized_img = crutils.reduce_cr(cr_pixels, img.exposition_duration)
                lon, lat, height = calc_pos.calc_pos(img)

                stats = crstats.calculate(crs, normalized_img)
                print(stats)

                end = time.time()

                print('Complete pipeline for %s image took %r seconds' % (instr, end - start))

            else:
                assert False, "Couldn't open %s" % filename


if __name__ == '__main__':
    unittest.main()
