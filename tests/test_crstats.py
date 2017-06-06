import unittest
import os, os.path, sys

from scipy.misc import imsave

from common.instruments import InstrumentUtils
from lib import calc_pos, crutils, crstats
from tests import utils

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCrStatsMethods(unittest.TestCase):

    test_images = utils.stats_images

    def test_cr_stats(self):

        for instr, filename in self.test_images.items():

            if os.path.isfile(filename):
                ins = InstrumentUtils.instrument_from_name(instr)
                pos_filename = filename.replace(ins.DATA_FILE_EXT[0], ins.POS_FILE_EXT)
                img = crutils.load(filename, pos_filename)

                clean, cr_pixels = crutils.clean_cr(img.data, None, 1)

                exp_time = img.exposition_duration  # seconds
                crs, normalized_img = crutils.reduce_cr(cr_pixels, exp_time)

                stats = crstats.calculate(crs, normalized_img)

                for key, value in stats.items():
                    print("{} is {}".format(key, value))

            else:
                assert False, "Couldn't open %s" % filename


if __name__ == '__main__':
    unittest.main()

#
#      /  RESULTS OF THE ANALYSIS OF COSMIC RAYS (CR)
#
# NUMCR   = 28      / Number of CR/sec
# MEALENCR= 4.521609      / Mean length of CR in pixels
# STDLENCR= 4.784670      / Std of the length of CR in pixels
# SWELENCR= 14.190257      / Skewness of the length of CR in pixels
# TOTFLUCR= 70494.1875      / Total flux of CR in ADUs/sec
# MEAFLUCR= 6.80052      / Mean flux of CR in ADUs/sec
# STDFLUCR= 44.2086      / Std of the flux of CR in ADUs/sec
# SKWFLUCR= 60.6605      / Skewness of the flux of CR in ADUs/sec

# #