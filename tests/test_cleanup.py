import unittest
import os, os.path, sys
import numpy

from lib import crutils
from common.image import ImageExtension, Image

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCleanupMethods(unittest.TestCase):
    def test_parse_raw(self):
        filename = os.path.join(os.path.dirname(__file__), 'test_raw.fits')

        # only try to open file if it exists
        if os.path.isfile(filename):
            img = crutils.load(filename)

            assert img.bitpix == 16
            assert img.file_type == 'SCI', "file type is %r" % img.file_type
            assert img.charge_inject == "NONE", "charge inject is %r" % img.charge_inject
            assert img.flash_current == "ZERO", "flash current is %r " % img.flash_current
            assert img.target_name == "DARK", "target name is %r" % img.target_name
            assert img.is_dark, "img type is %r " % img.target_name
            assert img.data is not None
            assert img.exposition_time == 360, "exposition time is %r" % img.exposition_time

            # Test extensions
            assert len(img.extension_info) == 5, "Extensions count is %r" % len(img.extension_info)
            sci_1_ext = img.extension(ImageExtension("SCI", "IMAGE", 1))
            assert sci_1_ext.get("XTENSION") == "IMAGE", "extension name is %r" % sci_1_ext.get("XTENSION")
            assert img.extension(ImageExtension("DOESNT", "EXISTS", 2)) is None

            with self.assertRaises(AssertionError):
                Image(img.data, None)

    def test_lacosmic(self):
        filename = os.path.join(os.path.dirname(__file__), 'test_raw.fits')
        mask_filename = os.path.join(os.path.dirname(__file__), 'mask.fits')
        # only try to open file if it exists
        if os.path.isfile(filename):
            img = crutils.load(filename)
            #mask = crutils.load(mask_filename)

            # print(mask.data)
            clean, cr_pixels = crutils.clean_cr(img.data, None, 1)

            # Remove found CRs from original image...
            diff = numpy.array(numpy.subtract(img.data, clean))

            # I should find some cosmic rays...
            cr = len(numpy.where(diff > 0)[0])

            # CR count must be the mask returned by script
            assert cr == numpy.sum(cr_pixels), "I found %r cr pixels" % cr

    def test_cr_stats(self):
        filename = os.path.join(os.path.dirname(__file__), 'test_raw.fits')
        if os.path.isfile(filename):
            img = crutils.load(filename)
            _, cr_pixels = crutils.clean_cr(img.data, None, 1)

            crs = crutils.reduce_cr(cr_pixels, img.exposition_time)

            assert len(crs) == 12060, "I found %r cosmic rays" % len(crs)

            for cr in crs:
                print("label:{}, area:{}".format(cr.label, cr.area))

if __name__ == '__main__':
    unittest.main()
