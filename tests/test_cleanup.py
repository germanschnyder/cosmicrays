import unittest
import os, os.path, sys

from app import cleanup
from app.image import ImageExtension, Image

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCleanupMethods(unittest.TestCase):
    def test_parse_raw(self):
        filename = os.path.join(os.path.dirname(__file__), 'test_raw.fits')

        # only try to open file if it exists
        if os.path.isfile(filename):
            img = cleanup.load(filename)

            assert img.bitpix == 16
            assert img.file_type == 'SCI', "file type is %r" % img.file_type
            assert img.charge_inject == "NONE", "charge inject is %r" % img.charge_inject
            assert img.flash_current == "ZERO", "flash current is %r " % img.flash_current
            assert img.target_name == "DARK", "target name is %r" % img.target_name
            assert img.is_dark, "img type is %r " % img.target_name
            assert img.data is not None

            # Test extensions
            assert len(img.extension_info) == 5, "Extensions count is %r" % len(img.extension_info)
            sci_1_ext = img.extension(ImageExtension("SCI", "IMAGE", 1))
            assert sci_1_ext.get("XTENSION") == "IMAGE", "extension name is %r" % sci_1_ext.get("XTENSION")
            assert img.extension(ImageExtension("DOESNT", "EXISTS", 2)) is None

            with self.assertRaises(AssertionError):
                Image(img.data, None)

if __name__ == '__main__':
    unittest.main()
