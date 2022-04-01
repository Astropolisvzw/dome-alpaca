import unittest
from dome_calc import DomeCalc
from dome_calc import DomePos
import logging
from utils import Relay
from decimal import *
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
        print(f"{calc}")
        assert calc.home_pos.az == 180
        assert calc.park_pos.is_complete()

    def test_dome_calc_domepos(self):
        calc = DomeCalc()
        park = DomePos(steps=10, turns=9)
        home = DomePos(steps=100, turns=90)
        calc.update_params(park, home, steps_per_turn=1000, turns_per_rotation=36)
        calc.sync_on_position(home, 180)
        # test calculations with domepos
        assert calc.get_domepos_az(140).az == 140
        assert calc.get_steps_turns(calc.get_rotpos(100, 5)) == (100, 5)

    def test_uncorrected_rotation_direction(self):
        calc = DomeCalc()
        park = DomePos(steps=10, turns=9)
        home = DomePos(steps=100, turns=90)
        calc.update_params(park, home, steps_per_turn=1000, turns_per_rotation=36)
        calc.sync_on_position(home, 180)

        rotation = calc.uncorrected_rotation_direction(90, 100)
        assert rotation == 10

        rotation = calc.uncorrected_rotation_direction(90, 350)
        assert rotation == -100

        rotation = calc.uncorrected_rotation_direction(350, 10)
        assert rotation == 20

        rotation = calc.uncorrected_rotation_direction(359, 0)
        assert rotation == 1

        rotation = calc.uncorrected_rotation_direction(0, 180)
        assert rotation == -180

        rotation = calc.uncorrected_rotation_direction(10, 359)
        assert rotation == 11

    def test_corrected_rotation_direction(self):
        calc = DomeCalc()
        park = DomePos(steps=10, turns=9)
        home = DomePos(steps=100, turns=90)
        calc.update_params(park, home, steps_per_turn=1000, turns_per_rotation=36)
        calc.sync_on_position(home, 180)
        LIMITS  = {Relay.LEFT_IDX: 180, Relay.RIGHT_IDX: 180}
        limitcounter = 0

        rotation = calc.corrected_rotation_direction(10, LIMITS, limitcounter)
        assert LIMITS[Relay.LEFT_IDX] == LIMITS[Relay.RIGHT_IDX] == 180
        assert rotation == 10

        limitcounter = 10
        rotation = calc.corrected_rotation_direction(200, LIMITS, limitcounter)
        assert rotation == -160

        limitcounter = -150
        rotation = calc.corrected_rotation_direction(-30, LIMITS, limitcounter)
        assert rotation == -30

        limitcounter = -180
        rotation = calc.corrected_rotation_direction(-1, LIMITS, limitcounter)
        assert rotation == 359

        limitcounter = 179
        rotation = calc.corrected_rotation_direction(2, LIMITS, limitcounter)
        assert rotation == -358


    def test_get_az(self):
        calc = DomeCalc()
        park = DomePos(steps=10, turns=9)
        home = DomePos(steps=100, turns=90)
        calc.update_params(park, home, steps_per_turn=1000, turns_per_rotation=36)
        calc.sync_on_position(home, 180)
        assert calc.get_az(home.rotpos) == 180
        assert calc.get_az(calc.north_pos.rotpos) == 0
        print(calc.get_az(Decimal(home.rotpos)+181*calc.turn_per_degree))

        assert calc.get_az(Decimal(home.rotpos)+Decimal(181)*Decimal(calc.turn_per_degree)) == 1
        # negative azimuths should be converted to 0-360
        print("result is",calc.get_az(Decimal(calc.north_pos.rotpos)-(Decimal(5)*Decimal(calc.turn_per_degree))))
        assert calc.get_az(Decimal(calc.north_pos.rotpos)-(Decimal(5)*Decimal(calc.turn_per_degree))) == 355




if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(asctime)s %(name)s: %(levelname)s %(message)s")
    unittest.main()
