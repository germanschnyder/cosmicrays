import unittest
from filter import cleanup


class TestCleanupMethods(unittest.TestCase):
    def test_parse(self):
        filename = 'test_raw.fits'
        output = cleanup.load(filename)

        print(output)
    # check that s.split fails when the separator is not a string
    # with self.assertRaises(TypeError):
    #    s.split(2)


if __name__ == '__main__':
    unittest.main()
