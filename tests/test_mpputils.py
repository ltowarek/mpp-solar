import unittest
from mppsolar import mpputils
from mppsolar import mppcommands


class test_mpputils(unittest.TestCase):
    def test_failed_initialisation(self):
        """ Initialisation should fail if no device provided """
        self.assertRaises(mppcommands.NoDeviceError, mpputils.mppUtils)
