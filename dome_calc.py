import logging
from collections import namedtuple
from dataclasses import dataclass

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
    LEFT = 1
    RIGHT = 2

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
        print(f"steps_turn_to_az({steps=}, {turns=}) - {rotpos=}, {rotpos-self.north_rotpos=}")
        return DomePos(az=((rotpos - self.north_rotpos)*self.degree_per_turn) % 360, steps=steps, turns=turns)

    def rotation_direction(self, current_az, target_az):
        direction = 0
        diff = abs(current_az - target_az)
        if diff == 0:
            direction = 0
        if diff < 180:
            # Rotate current directly towards target.
            direction = self.RIGHT if current_az < target_az else self.LEFT;
        else:
            # Rotate the other direction towards target.
            direction = self.LEFT if current_az < target_az else self.RIGHT;
        print(f"Currentaz = {current_az}, {target_az=}")
        return direction, diff
