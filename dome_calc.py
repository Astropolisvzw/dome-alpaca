import logging
from collections import namedtuple
from dataclasses import dataclass
from utils import RELAY_DOWN_IDX, RELAY_UP_IDX, RELAY_LEFT_IDX, RELAY_RIGHT_IDX

@dataclass
class DomePos:
    az: int = 0
    alt: int = 0
    steps: int = 0
    turns: int = 0
    rotpos: float = 0


class DomeCalc:
    park_pos: DomePos = None
    home_pos: DomePos = None
    north_pos: DomePos = None
    steps_per_turn = 0
    turns_per_rotation = 0
    degree_per_turn = 0
    degree_per_step = 0
    turn_per_degree = 0
    LEFT = RELAY_LEFT_IDX
    RIGHT = RELAY_RIGHT_IDX

    def __init__(self):
        return

    def update_params(self, park_pos: DomePos, home_pos: DomePos, steps_per_turn, turns_per_rotation):
        self.park_pos = park_pos
        self.home_pos = home_pos
        self.north_pos = DomePos()
        self.steps_per_turn = steps_per_turn
        self.turns_per_rotation = turns_per_rotation
        self.degree_per_turn = 360/turns_per_rotation
        self.degree_per_step = self.degree_per_turn/steps_per_turn
        self.turn_per_degree = turns_per_rotation/360
        self.home_pos.rotpos = self.get_rotpos(home_pos.steps, home_pos.turns)
        self.north_pos.rotpos = self.home_pos.rotpos + ((0 - home_pos.az)/self.degree_per_turn)


    def get_rotpos(self, steps, turns):
        logging.debug(f"get_rotpos({steps/self.steps_per_turn=}, {turns=})")
        return steps/self.steps_per_turn + turns

    def steps_turn_to_pos(self, steps, turns):
        rotpos = self.get_rotpos(steps, turns)
        result = DomePos(az=((rotpos - self.north_pos.rotpos)*self.degree_per_turn) % 360, steps=steps, turns=turns)
        logging.info(f"Arduino to degrees: {result.az} deg ({steps=}, {turns=})")
        return DomePos(az=((rotpos - self.north_pos.rotpos)*self.degree_per_turn) % 360, steps=steps, turns=turns)

    def rotation_direction(self, current_az, target_az, limits, limitscounter):
        LEFT = self.LEFT
        RIGHT= self.RIGHT
        diff1 = (target_az - current_az)%360
        if diff1 == 0:
            direction = RIGHT
            diff = 0
        if diff1 == 180:
            logging.info("180 degrees, going towards the shortest cable")
            direction = RIGHT if limitscounter[RIGHT] < abs(limitscounter[LEFT]) else LEFT
        if current_az + 180 > target_az:
            # Rotate current directly towards target.
            direction = RIGHT
            diff = diff1
        else:
            # Rotate the other direction towards target.
            direction = LEFT
            diff = current_az + 360 - target_az

        logging.info(f"Orig result: {'LEFT' if direction==LEFT else 'RIGHT'}, {diff1=}, {diff=}, {str(limitscounter)=}")
        if direction == LEFT:
            total_left = limitscounter[LEFT] - diff
            logging.info(f"{total_left=}, {limitscounter[RIGHT]=}")
            if total_left+limitscounter[RIGHT] < limits[LEFT]:
                logging.info("cable length violation")
                direction = RIGHT
                diff = 360 - diff
                limitscounter[RIGHT] = limitscounter[RIGHT] + diff
        else:
            total_right = limitscounter[RIGHT] + diff
            logging.info(f"{limitscounter[LEFT]=}, {total_right=}")
            if limitscounter[LEFT]+total_right > limits[RIGHT]:
                logging.info("cable length violation")
                direction = LEFT
                diff = 360 - diff
                limitscounter[LEFT] = limitscounter[LEFT] + diff

        logging.info(f"result: {'LEFT' if direction==LEFT else 'RIGHT'}, {diff1=}, {diff=}, {str(limitscounter)=}")
        return direction, diff
