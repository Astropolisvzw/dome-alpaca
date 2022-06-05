import logging
from dataclasses import dataclass
import utils
from utils import Relay
import decimal
from decimal import Decimal


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
    park_pos: DomePos
    home_pos: DomePos
    north_pos: DomePos
    steps_per_turn: Decimal = Decimal(0)
    turns_per_rotation: Decimal = Decimal(0)
    degree_per_turn: Decimal = Decimal(0)
    degree_per_step: Decimal = Decimal(0)
    turn_per_degree: Decimal = Decimal(0)
    LEFT = Relay.LEFT_IDX
    RIGHT = Relay.RIGHT_IDX

    def __init__(self):
        # init python Decimals so we can calculate more precisely
        c = decimal.getcontext()
        # c.traps[decimal.FloatOperation] = True
        c.prec = 7

    def update_params(self, park_pos: DomePos, home_pos: DomePos, steps_per_turn, turns_per_rotation):
        """ Call this method before first use of the class. Initialises all parameters necessory for dome calculations """
        # params
        self.steps_per_turn = Decimal(steps_per_turn)
        self.turns_per_rotation = Decimal(turns_per_rotation)
        self.degree_per_turn = Decimal(360)/self.turns_per_rotation
        self.degree_per_step = self.degree_per_turn/self.steps_per_turn
        self.turn_per_degree = self.turns_per_rotation/Decimal(360)

        # positions (possibly incomplete, no az/rotpos until after sync_on_position call)
        self.park_pos = park_pos
        self.home_pos = home_pos
        self.north_pos = DomePos()

    # given that sync_pos has azimuth sync_az, calculate our NORTH position
    def sync_on_position(self, sync_pos: DomePos, sync_az: float):
        """ assume the current encoder position (sync_pos) is at sync_az, then calculate the North position """
        # correcting the incoming sync position. The AZ will be rubbish, but at least the rotpos will be correct
        self.complete_domepos(sync_pos)
        # logging.info(f"{sync_pos.rotpos=} - ({sync_az=}/{self.degree_per_turn=})")
        self.north_pos.rotpos = float(Decimal(sync_pos.rotpos) - (Decimal(sync_az)/self.degree_per_turn))
        self.north_pos.az = 0
        self.north_pos.turns = int(self.north_pos.rotpos)
        self.north_pos.steps = int(Decimal(self.north_pos.rotpos - self.north_pos.turns) * self.steps_per_turn)
        self.complete_domepos(self.home_pos)
        self.complete_domepos(self.park_pos)
        self.complete_domepos(sync_pos)
        print(f"sync on position: {sync_pos=}")
        return sync_pos

    # creates an is_complete domepos using only steps and turns (+ a fully inited calc class)
    def get_domepos(self, steps, turns):
        rotpos=self.get_rotpos(steps, turns)
        az = self.get_az(rotpos)
        result = DomePos(steps=steps, turns=turns, az=az, rotpos=rotpos)
        logging.info(f"Creating domepos for steps and turns: {result.az} deg ({steps=}, {turns=}, {rotpos=})")
        return result

    # get a domepos with a given az
    def get_domepos_az(self, az):
        rotpos=Decimal(az) / self.degree_per_turn + Decimal(self.north_pos.rotpos)
        steps, turns = self.get_steps_turns(rotpos)
        result = DomePos(steps=int(steps), turns=turns, az=az, rotpos=float(rotpos))
        logging.info(f"Creating domepos for az: {result.az} deg ({steps=}, {turns=}, {rotpos=})")
        return result

    def complete_domepos(self, domepos: DomePos):
        """ takes a DomePos and fills in (in-place) the rotpos and az """
        domepos.rotpos=self.get_rotpos(domepos.steps, domepos.turns)
        domepos.az = self.get_az(domepos.rotpos)

    def get_rotpos(self, steps, turns):
        """ takes steps and turns and calculates the rotpos """
        logging.debug(f"get_rotpos({Decimal(steps)/self.steps_per_turn=}, {turns=})")
        return float(Decimal(steps)/self.steps_per_turn + Decimal(turns))

    def get_steps_turns(self, rotpos):
        """ takes steps and turns and calculates the rotpos """
        return float(Decimal(rotpos - int(rotpos))*self.steps_per_turn), int(rotpos)

    def get_az(self, rotpos) -> float:
        """ calculates the azimuth given a rotpos """
        result = float(((Decimal(rotpos) - Decimal(self.north_pos.rotpos))*Decimal(self.degree_per_turn)) % Decimal(360))
        # % doesn't work with decimals (returns negative degrees) so we convert before returning
        return float(result) % 360


    def rotation_direction(self, current_az, target_az, limits, limitscounter):
        """ determine rotation direction and the remaining difference in azimuth """
        rotation = self.uncorrected_rotation_direction(current_az, target_az)
        return self.corrected_rotation_direction(rotation, limits, limitscounter)


    def uncorrected_rotation_direction(self, current_az, target_az):
        """ calculates which direction the dome should turn """
        rotation = utils.best_rotation(current_az, target_az)
        logging.info(f"uncorrected_rotation_direction result: {rotation}")
        return rotation


    def corrected_rotation_direction(self, rotation, limits, limitscounter):
        """ corrects dome rotation according to the current cable limits """
        direction = utils.rotation_to_direction(rotation)
        limit = limits[direction]
        newrotation = abs(rotation)
        if abs(limitscounter + rotation) > limit:
            direction = utils.direction_invert(direction)
            newrotation = (360 + rotation)%360
        logging.info(f"corrected_rotation_direction result: {rotation=}, {newrotation=}, {limitscounter=}")
        return newrotation

    def __repr__(self):
        return f"DomeCalc Class:\n{self.park_pos=}\n{self.north_pos=}\n{self.home_pos=}\n{self.steps_per_turn=}\n \
            {self.turns_per_rotation=}\n{self.degree_per_turn=}\n{self.degree_per_step=}\n{self.turn_per_degree=}\n"
