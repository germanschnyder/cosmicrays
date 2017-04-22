import unittest
import os, os.path, sys
import math

import time

from common.instruments import WFPC2, ACS, WFC3, STIS, NICMOS, InstrumentUtils
from lib import calc_pos, crutils

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCalcPosMethods(unittest.TestCase):

    test_images = {
        'ACS': os.path.join(os.path.dirname(__file__), 'images/ACS/j6mf16lhq_%s.fits' % ACS.DATA_FILE_EXT[0]),
        'WFC3': os.path.join(os.path.dirname(__file__), 'images/WFC3/iaa901jxq_%s.fits' % WFC3.DATA_FILE_EXT[0]),
        'STIS': os.path.join(os.path.dirname(__file__), 'images/STIS/o3sj01ozq_%s.fits' % STIS.DATA_FILE_EXT[0]),
        'WFPC2': os.path.join(os.path.dirname(__file__), 'images/WFPC2/u21u0201t_%s.fits' % WFPC2.DATA_FILE_EXT[0]),
        'NICMOS': os.path.join(os.path.dirname(__file__), 'images/NICMOS/n3t102d3q_%s.fits' % NICMOS.DATA_FILE_EXT[0])
    }

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

    def test_pipeline(self):
        for instr, filename in self.test_images.items():

            if os.path.isfile(filename):
                ins = InstrumentUtils.instrument_from_name(instr)
                pos_filename = filename.replace(ins.DATA_FILE_EXT[0], ins.POS_FILE_EXT)
                start = time.time()
                img = crutils.load(filename, pos_filename)
                _, cr_pixels = crutils.clean_cr(img.data, None, 1)

                crs = crutils.reduce_cr(cr_pixels, img.exposition_duration)
                lon, lat, height = calc_pos.calc_pos(img)
                end = time.time()

                print('Complete pipeline for %s image took %r seconds' % (instr, end - start))

            else:
                assert False, "Couldn't open %s" % filename


if __name__ == '__main__':
    unittest.main()
