import unittest
from dome import Dome
from dome_calc import DomePos
import logging
from utils import Relay
from decimal import *

class TestDomeCalc(unittest.TestCase):
    def setUp(self):
        self.test = "test"

    def test_dome_calc(self):
        dome = Dome()
        res = dome.slew_to_az(-10)
        assert res is not None
        assert dome.slew_to_az(10) == None


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    unittest.main()
