import unittest
import logging
import utils

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test = "test"

    def test_smallest_diff(self):
        assert utils.smallest_diff(90, 180) == 90

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    unittest.main()
