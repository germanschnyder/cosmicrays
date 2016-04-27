import unittest
import os, sys
from filter import cleanup

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), sys.argv[0]))


class TestCleanupMethods(unittest.TestCase):

    def test_parse(self):
       # filename = os.path.join(__location__, 'test_raw.fits')
       # output = cleanup.load(filename)

       # print(output)
    # check that s.split fails when the separator is not a string
    # with self.assertRaises(TypeError):
    #    s.split(2)

        assert 1 == 1


if __name__ == '__main__':
    unittest.main()
