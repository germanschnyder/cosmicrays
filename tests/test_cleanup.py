import unittest
import os, os.path, sys
import numpy

from common.instruments import WFC3, ACS, STIS, WFPC2, InstrumentUtils, NICMOS
from lib import crutils
from common.image import ImageExtension, Image
from tests import utils

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


def _lacosmic_for_type(filename, instrument):
    if os.path.isfile(filename):

        pos_filename = filename.replace(instrument.DATA_FILE_EXT[0], instrument.POS_FILE_EXT)

        img = crutils.load(filename, pos_filename)

        assert img.data.shape[0] == instrument.WIDTH, "width is %s instead of %s" % (img.data.shape[0], instrument.WIDTH)
        assert img.data.shape[1] == instrument.HEIGHT, "height is %s instead of %s" % (img.data.shape[1], instrument.HEIGHT)

        # print(mask.data)
        clean, cr_pixels = crutils.clean_cr(img.data, None, 1)

        # Remove found CRs from original image...
        diff = numpy.array(numpy.subtract(img.data, clean))

        # I should find some cosmic rays...
        cr = len(numpy.where(diff > 0)[0])

        # cr count from calculated mask
        mask_cr = numpy.sum(cr_pixels)

        # CR count must be the mask returned by script
        assert cr == mask_cr, "I found %r cr pixels instead of %r, difference is %r" % (cr, mask_cr, mask_cr - cr)
    else:
        assert False, "Couldn't open %s" % filename


class TestCleanupMethods(unittest.TestCase):

    test_images = utils.test_images

    def test_instrument_detection(self):
        for (instr, filename) in self.test_images.items():

            # only try to open file if it exists
            if os.path.isfile(filename):
                ins = InstrumentUtils.instrument_from_name(instr)
                pos_filename = filename.replace(ins.DATA_FILE_EXT[0], ins.POS_FILE_EXT)

                img = crutils.load(filename, pos_filename)

                assert InstrumentUtils.instrument_from_name(instr) == img.instrument
            else:
                assert False, "Couldn't open %s" % filename

    def test_basic_params(self):
        for instr, filename in self.test_images.items():

            # only try to open file if it exists
            if os.path.isfile(filename):
                ins = InstrumentUtils.instrument_from_name(instr)
                pos_filename = filename.replace(ins.DATA_FILE_EXT[0], ins.POS_FILE_EXT)

                print("Loading %s and %s" % (filename, pos_filename))

                img = crutils.load(filename, pos_filename)

                assert img.exposition_duration is not None, "exposition duration is %r for %s" % (img.exposition_duration, filename)
                assert img.observation_date is not None, "observation date is %s" % img.observation_date
                assert img.observation_start_time is not None, "observation start time is %s" % img.observation_start_time
                assert img.proposal_id is not None, "proposal id is %s" % img.proposal_id

                assert img.position_angle is not None, "position angle is %s" % img.position_angle
                assert img.right_ascension is not None, "right ascension is %s" % img.right_ascension
                assert img.declination is not None, "declination is %s" % img.declination

                if img.aperture is None:
                    assert img.ecliptic_lat is None, "ecliptic latitude is %s" % img.ecliptic_lat
                    assert img.ecliptic_lon is None, "ecliptic longitude is %s" % img.ecliptic_lon
                    assert img.galactic_lat is None, "galactic latitude is %s" % img.galactic_lat
                    assert img.galactic_lon is None, "galactic longitude is %s" % img.galactic_lon
                else:
                    assert img.ecliptic_lat is not None, "ecliptic latitude is %s" % img.ecliptic_lat
                    assert img.ecliptic_lon is not None, "ecliptic longitude is %s" % img.ecliptic_lon
                    assert img.galactic_lat is not None, "galactic latitude is %s" % img.galactic_lat
                    assert img.galactic_lon is not None, "galactic longitude is %s" % img.galactic_lon

                assert img.postnstx is not None, "postnstx is %s for %s" % (img.postnstx, filename)
                assert img.postnsty is not None, "postnsty is %s for %s" % (img.postnsty, filename)
                assert img.postnstz is not None, "postnstz is %s for %s" % (img.postnstz, filename)

            else:
                assert False, "Couldn't open %s" % filename

    def test_data_file(self):
        filename = self.test_images.get(WFC3.NAME)

        # only try to open file if it exists
        if os.path.isfile(filename):

            pos_filename = filename.replace(WFC3.DATA_FILE_EXT[0], WFC3.POS_FILE_EXT)

            img = crutils.load(filename, pos_filename)

            # Test regular attributes

            assert img.bitpix == 16
            assert img.observation_set == 'iaa901jxq', "observation set is %s" % img.observation_set
            assert img.file_name == 'iaa901jxq_flt.fits', "file name is %s" % img.file_name
            assert img.file_type == 'SCI', "file type is %r" % img.file_type
            assert img.charge_inject == "NONE", "charge inject is %r" % img.charge_inject
            assert img.flash_current == "ZERO", "flash current is %r " % img.flash_current
            assert img.target_name == "DARK", "target name is %r" % img.target_name
            assert img.is_dark, "img type is %r " % img.target_name
            assert img.instrument == WFC3, "img instrument is %s" % img.instrument
            assert img.data is not None
            assert img.observation_date == "2009-06-30", "observation date is %s" % img.observation_date
            assert img.observation_start_time == "09:18:39", "observation start time is %s" % img.observation_start_time
            assert img.exposition_duration == 360, "exposition duration is %r" % img.exposition_duration
            assert img.right_ascension_target == 0.0, "right ascension target is %s"% img.right_ascension_target

            # Test WCS attributes
            assert img.wcs_axes == 2
            assert img.wcs_dec_aperture == 70.29782637001, "wcs declination aperture is %r" % img.wcs_dec_aperture
            assert img.wcs_cd(1, 1) == -1.04411e-05, "wcs cd 1-1 is %r" % img.wcs_cd(1, 1)
            assert img.wcs_cd(666, 666) is None

            # Test extensions
            assert len(img.extension_info) == 5, "Extensions count is %r" % len(img.extension_info)

            # SCI extension
            sci_1_ext = img.extension(ImageExtension("SCI", "IMAGE", 1))
            assert sci_1_ext.get("XTENSION") == "IMAGE", "extension type is %r" % sci_1_ext.get("XTENSION")
            assert sci_1_ext.get("NAXIS1") == 4096, "x axis length is %s" % sci_1_ext.get("NAXIS1")
            assert sci_1_ext.get("NAXIS2") == 2051, "y axis length is %s" % sci_1_ext.get("NAXIS2")

            # ERR extension
            err_ext = img.extension(ImageExtension("ERR", "IMAGE", 1))
            assert err_ext.get("NAXIS") == 2, "axis count is %s" % err_ext.get("NAXIS")

            # DQ extension
            dq_ext = img.extension(ImageExtension("DQ", "IMAGE", 1))
            assert dq_ext.get("NAXIS") == 2, "axis count is %s" % dq_ext.get("NAXIS")

            # non existant extension
            assert img.extension(ImageExtension("DOESNT", "EXISTS", 2)) is None

            with self.assertRaises(AssertionError):
                Image(img.data, None, None)

        else:
            assert False, "Couldn't open %s" % filename

    def test_lacosmic_acs(self):
        filename = self.test_images.get('ACS')
        _lacosmic_for_type(filename, ACS)

    def test_lacosmic_wfc3(self):
        filename = self.test_images.get('WFC3')
        _lacosmic_for_type(filename, WFC3)

    def test_lacosmic_stis(self):
        filename = self.test_images.get('STIS')
        _lacosmic_for_type(filename, STIS)

    def test_lacosmic_wfpc2(self):
        filename = self.test_images.get('WFPC2')
        _lacosmic_for_type(filename, WFPC2)

    def test_lacosmic_nicmos(self):
        filename = self.test_images.get(NICMOS.NAME)
        _lacosmic_for_type(filename, NICMOS)

    def test_cr_clean_and_reduce(self):
        numpy.set_printoptions(threshold=numpy.nan)

        cr_pixels = numpy.matrix([
            [False, False,  True],
            [True,  True,   False],
            [False, False,  True],
            [False, True,   True]
        ])

        crs = crutils.reduce_cr(cr_pixels, 1000)

        assert 3 == len(crs), "There are %d cosmic rays" % len(crs)

        # Now, from file
        cr_pixels = numpy.load(os.path.join(os.path.dirname(__file__), "images/500x500.npy")).astype(int)
        crs = crutils.reduce_cr(cr_pixels, 1000)

        assert numpy.sum(cr_pixels) > len(crs), "There are more cr (%r) than pixels (%r)" % (len(crs), numpy.sum(cr_pixels))
        assert 780 == len(crs), "There are %d cosmic rays" % len(crs)

    def test_cr_stats(self):
        for instr, filename in self.test_images.items():
            if os.path.isfile(filename):
                numpy.set_printoptions(threshold=numpy.nan)

                ins = InstrumentUtils.instrument_from_name(instr)
                pos_filename = filename.replace(ins.DATA_FILE_EXT[0], ins.POS_FILE_EXT)

                img = crutils.load(filename, pos_filename)
                _, cr_pixels = crutils.clean_cr(img.data, None, 1)

                crs = crutils.reduce_cr(cr_pixels, img.exposition_duration)

                print("Just found %r cosmic rays" % len(crs))

            else:
                assert False, "Couldn't open %s" % filename


if __name__ == '__main__':
    unittest.main()
