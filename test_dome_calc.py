import unittest
from dome_calc import DomeCalc
from dome_calc import DomePos
import logging
from utils import Relay

class TestDomeCalc(unittest.TestCase):
    def setUp(self):
        self.test = "test"

    def test_dome_pos(self):
        raw = DomePos()
        assert raw.steps == -1
        assert raw.turns == -1
        raw1 = DomePos(steps=10, turns=9)
        assert raw1.steps == 10
        assert raw1.turns == 9
        raw2 = DomePos(steps=100)
        assert raw2.steps == 100
        assert raw2.turns == -1

    def test_dome_calc(self):
        calc = DomeCalc()
        park = DomePos(steps=10, turns=9)
        home = DomePos(steps=100, turns=90)
        calc.update_params(park, home, steps_per_turn=1000, turns_per_rotation=36)
        calc.sync_on_position(home, 180)
        # test update_params and sync_on_position
        assert calc.home_pos == home
        assert calc.park_pos == park
        assert calc.north_pos is not None
        assert calc.north_pos.is_complete()
        assert calc.north_pos.az == 0
        assert calc.home_pos.is_complete()
        assert calc.home_pos.az == 180
        assert calc.park_pos.is_complete()

    def test_uncorrected_rotation_direction(self):
        calc = DomeCalc()
        park = DomePos(steps=10, turns=9)
        home = DomePos(steps=100, turns=90)
        calc.update_params(park, home, steps_per_turn=1000, turns_per_rotation=36)
        calc.sync_on_position(home, 180)

        dir, diff = calc.uncorrected_rotation_direction(90, 100)
        assert dir == Relay.RIGHT_IDX and diff == 10

        dir, diff = calc.uncorrected_rotation_direction(90, 350)
        assert dir == Relay.LEFT_IDX and diff == 100

        dir, diff = calc.uncorrected_rotation_direction(350, 10)
        assert dir == Relay.RIGHT_IDX and diff == 20

        dir, diff = calc.uncorrected_rotation_direction(359, 0)
        assert dir == Relay.RIGHT_IDX and diff == 1

        dir, diff = calc.uncorrected_rotation_direction(0, 180)
        assert dir == Relay.LEFT_IDX and diff == 180

        dir, diff = calc.uncorrected_rotation_direction(10, 359)
        assert dir == Relay.LEFT_IDX and diff == 11

    def test_corrected_rotation_direction(self):
        calc = DomeCalc()
        park = DomePos(steps=10, turns=9)
        home = DomePos(steps=100, turns=90)
        calc.update_params(park, home, steps_per_turn=1000, turns_per_rotation=36)
        calc.sync_on_position(home, 180)
        LIMITS  = {RELAY_LEFT_IDX: 90, RELAY_RIGHT_IDX: 90}

        dir, diff = calc.corrected_rotation_direction(90, 100)
        assert dir == Relay.RIGHT_IDX and diff == 10

        dir, diff = calc.uncorrected_rotation_direction(90, 350)
        assert dir == Relay.LEFT_IDX and diff == 100

        dir, diff = calc.uncorrected_rotation_direction(350, 10)
        assert dir == Relay.RIGHT_IDX and diff == 20

        dir, diff = calc.uncorrected_rotation_direction(359, 0)
        assert dir == Relay.RIGHT_IDX and diff == 1

        dir, diff = calc.uncorrected_rotation_direction(0, 180)
        assert dir == Relay.LEFT_IDX and diff == 180

        dir, diff = calc.uncorrected_rotation_direction(10, 359)
        assert dir == Relay.LEFT_IDX and diff == 11

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    unittest.main()
