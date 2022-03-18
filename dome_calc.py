import logging
from dataclasses import dataclass
from utils import Relay
from typing import Tuple


@dataclass
class DomePos:
    """ Represents a dome position, where steps and turns is coming directly from the encoder, and az/rotpos are derived.
        In order to derive these values we need external data such as the number of steps per turn and the north position.
    """
    # don't change externally!
    steps: int = -1
    turns: int = -1
    az: float = -1
    # turns can be negative
    rotpos: float = -1

    # def __init__(self, steps, turns, az):
    #     self.steps = steps
    #     self.turns = turns
    #     self.az = az

    @property
    def alt(self) -> int:
        return 0

    def is_complete(self) -> bool:
        return self.steps != -1 and self.turns != -1 and self.az != -1 and self.rotpos != -1



class DomeCalc:
    """ Holds the current dome calculation parameters (read from disk).
        Provides methods to calculate the rotational position, azimuth and direction in which to slew.
    """
    park_pos: DomePos = None
    home_pos: DomePos = None
    north_pos: DomePos = None
    steps_per_turn = 0
    turns_per_rotation = 0
    degree_per_turn = 0
    degree_per_step = 0
    turn_per_degree = 0
    LEFT = Relay.LEFT_IDX
    RIGHT = Relay.RIGHT_IDX

    def __init__(self):
        return

    def update_params(self, park_pos: DomePos, home_pos: DomePos, steps_per_turn, turns_per_rotation):
        # params
        self.steps_per_turn = steps_per_turn
        self.turns_per_rotation = turns_per_rotation
        self.degree_per_turn = 360/turns_per_rotation
        self.degree_per_step = self.degree_per_turn/steps_per_turn
        self.turn_per_degree = turns_per_rotation/360

        # positions (possibly incomplete, no az/rotpos until after sync_on_position call)
        self.park_pos = park_pos
        self.home_pos = home_pos
        self.north_pos = DomePos()


    # given that sync_pos has azimuth sync_az, calculate our NORTH position
    def sync_on_position(self, sync_pos: DomePos, sync_az: float):
        # correcting the incoming sync position. The AZ will be rubbish, but at least the rotpos will be correct
        self.complete_domepos(sync_pos)
        # logging.info(f"{sync_pos.rotpos=} - ({sync_az=}/{self.degree_per_turn=})")
        self.north_pos.rotpos = sync_pos.rotpos - (sync_az/self.degree_per_turn)
        self.north_pos.az = 0
        self.north_pos.turns = int(self.north_pos.rotpos)
        self.north_pos.steps = (self.north_pos.rotpos - self.north_pos.turns) * self.steps_per_turn
        self.complete_domepos(self.home_pos)
        self.complete_domepos(self.park_pos)

    # creates an is_complete domepos using only steps and turns (+ a fully inited calc class)
    def get_domepos(self, steps, turns):
        rotpos=self.get_rotpos(steps, turns)
        az = self.get_az(rotpos)
        result = DomePos(steps=steps, turns=turns, az=az, rotpos=rotpos)
        logging.info(f"Encoder position to dome position: {result.az} deg ({steps=}, {turns=}, {rotpos=})")
        return result

    def complete_domepos(self, domepos: DomePos):
        """ takes a DomePos and fills in (in-place) the rotpos and az """
        domeposrrotpos=self.get_rotpos(domepos.steps, domepos.turns)
        domepos.az = self.get_az(domepos.rotpos)


    def get_rotpos(self, steps, turns):
        """ takes steps and turns and calculates the rotpos """
        logging.debug(f"get_rotpos({steps/self.steps_per_turn=}, {turns=})")
        return steps/self.steps_per_turn + turns

    def get_az(self, rotpos) -> int:
        """ calculates the azimuth given a rotpos """
        return ((rotpos - self.north_pos.rotpos)*self.degree_per_turn) % 360


    def rotation_direction(self, current_az, target_az, limits, limitscounter):
        """ determine rotation direction and the remaining difference in azimuth """
        direction, diff = self.uncorrected_rotation_direction(current_az, target_az)
        return self.corrected_rotation_direction(direction, diff, limits, limitscounter)

    def uncorrected_rotation_direction(self, current_az, target_az):
        """ calculates which direction the dome should turn """
        diff1 = (target_az - current_az)%360
        if diff1 == 0:
            direction = Relay.RIGHT_IDX
            diff = 0
        if diff1 == 180:
            direction = Relay.LEFT_IDX
            diff = diff1
        if current_az + 180 > target_az:
            # Rotate current directly towards target.
            direction = Relay.RIGHT_IDX
            diff = diff1
        else:
            # Rotate the other direction towards target.
            direction = Relay.LEFT_IDX
            diff = current_az + 360 - target_az
        logging.info(f"Orig result: {direction}, {diff1=}, {diff=}")
        return direction, diff

    def corrected_rotation_direction(self, direction, diff, limits, limitscounter):
        """ corrects dome rotation according to the current cable limits """
        LEFT = 0
        RIGHT= 1
        total_direction = limitscounter[direction] + diff
        if direction == Relay.LEFT_IDX:
            logging.info(f"{total_direction=}, {limitscounter=}")
            if total_direction-limitscounter[Relay.RIGHT_IDX] > limits[LEFT]:
                logging.info("cable length violation")
                direction = Relay.RIGHT_IDX
                diff = 360 - diff
        else:
            logging.info(f"{limitscounter=}, {total_direction=}")
            if limitscounter[Relay.RIGHT_IDX]-total_direction > limits[RIGHT]:
                logging.info("cable length violation")
                direction = Relay.LEFT_IDX
                diff = 360 - diff

        logging.info(f"result: {'LEFT' if direction==LEFT else 'RIGHT'}, {diff=}, {str(limitscounter)=}")
        return direction, diff
