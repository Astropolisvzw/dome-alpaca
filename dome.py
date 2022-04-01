from arduino_serial import ArduinoSerial
from configparser import ConfigParser
import logging
from dome_calc import DomeCalc
from dome_calc import DomePos
import os
from utils import synchronized_method
from time import sleep
from datetime import datetime
import cachetools.func
from multiprocessing import Manager
from threading import Thread
from utils import Relay
import utils

class Dome:
    connected = False
    slaved = False
    curr_pos: DomePos = None
    serial_port: str = None
    serial_baud: int = None
    mc_serial: ArduinoSerial = None
    dome_calc = DomeCalc()
    config_file: str = ''
    LIMITS  = {Relay.LEFT_IDX: 180, Relay.RIGHT_IDX: 180} # should be static
    conformance = False

    manager = Manager()
    ns = manager.Namespace()
    # 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error
    ns.shutter = 1
    ns.slewing = False
    ns.domeslewing = False
    ns.aborted = False
    ns.target_az = 180 # set initial slewing target to SOUTH, should be overwritten and never used
    ns.limitcounter = 0 # no cable is used either left or right at the start of operation. Dome should be in HOME position

    def __init__(self, config_file='ap_ashdome_config.ini', conformance=False):
        self.config_file = config_file
        park_pos, home_pos, spt, tpr, serial_port, serial_baud = self.load_settings()
        self.dome_calc.update_params(park_pos, home_pos, spt, tpr)
        self.dome_calc.sync_on_position(home_pos, home_pos.az)
        self.set_serial_port(serial_port, serial_baud)
        self.park_pos = park_pos
        self.home_pos = home_pos
        self.steps_per_turn = spt
        self.turns_per_rotation = tpr
        self.conformance = conformance
        logging.info(f"Inited dome with park: {self.dome_calc.park_pos}, home: {self.dome_calc.home_pos}, spt: {spt}, tpr: {tpr}, serial port: {serial_port}")

    def get_slewing(self):
        return self.ns.slewing

    def set_serial_port(self, serial_port, serial_baud):
        self.serial_port = serial_port
        self.serial_baud = serial_baud
        if self.mc_serial is not None:
           self.mc_serial.close()
        self.mc_serial = ArduinoSerial(serial_port, serial_baud)
        self._save_settings()

    def _save_settings(self):
        self.save_settings(self.dome_calc.park_pos, self.dome_calc.home_pos, self.dome_calc.steps_per_turn, self.dome_calc.turns_per_rotation, self.serial_port, self.serial_baud)

    def save_settings(self, park_pos, home_pos, spt, tpr, serial_port, serial_baud):
        config = ConfigParser()
        config.read(self.config_file)
        section = 'domeparams'
        config.set(section, 'park_az', str(park_pos.az))
        config.set(section, 'park_steps', str(park_pos.steps))
        config.set(section, 'park_turns', str(park_pos.turns))
        config.set(section, 'home_az', str(home_pos.az))
        config.set(section, 'home_steps', str(home_pos.steps))
        config.set(section, 'home_turns', str(home_pos.turns))
        config.set(section, 'open_shutter', str(self.open_shutter_seconds))
        config.set(section, 'close_shutter', str(self.close_shutter_seconds))
        config.set(section, 'steps_per_turn', str(spt))
        config.set(section, 'turns_per_rotation', str(tpr))
        config.set(section, 'serial_port', serial_port)
        config.set(section, 'serial_baud', str(serial_baud))
        with open(self.config_file, 'w') as f:
            config.write(f)

    def load_settings(self):
        if not os.path.isfile(self.config_file):
            logging.error(f"Couldn't find ini file {self.config_file}")
            self.save_settings(DomePos(), DomePos(), 0,0, 'serial', 9600)
            exit()
        config = ConfigParser()
        section = 'domeparams'
        config.read(self.config_file)
        park_az = config.getfloat(section, 'park_az')
        park_steps = config.getint(section, 'park_steps')
        park_turns = config.getint(section, 'park_turns')
        home_az = config.getfloat(section, 'home_az')
        home_steps = config.getint(section, 'home_steps')
        home_turns = config.getint(section, 'home_turns')
        self.open_shutter_seconds = config.getint(section, 'open_shutter')
        self.close_shutter_seconds = config.getint(section, 'close_shutter')
        spt = config.getint(section, 'steps_per_turn')
        tpr = config.getfloat(section, 'turns_per_rotation')
        serial_port = config.get(section, 'serial_port')
        serial_baud = config.getint(section, 'serial_baud')
        return DomePos(az=park_az, steps=park_steps, turns=park_turns), DomePos(az = home_az, steps=home_steps, turns=home_turns), spt, tpr, serial_port, serial_baud

    # get azimuth and check if it's near the home position
    def is_at_home(self, degree_tolerance: float = 0.5):
        self._update_azimuth()
        return abs(self.curr_pos.az - self.dome_calc.home_pos.az) < degree_tolerance

    # get azimuth and check if it's near the home position
    def is_at_park(self,  degree_tolerance: float = 0.5):
        self._update_azimuth()
        return abs(self.curr_pos.az - self.dome_calc.park_pos.az) < degree_tolerance

    # 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error
    def close_shutter(self):
        self.ns.aborted = False
        self.ns.shutter = 3
        self.ns.slewing = True
        slew_thread = Thread(target=self._shutter_action, args=(Relay.DOWN_IDX, self.close_shutter_seconds, 1))
        slew_thread.start()

    def abort_slew(self):
        self.mc_serial.disable_all_relays()
        self.ns.aborted = True

    def open_shutter(self):
        self.ns.aborted = False
        self.ns.shutter = 2
        self.ns.slewing = True
        slew_thread = Thread(target=self._shutter_action, args=(Relay.UP_IDX, self.close_shutter_seconds, 0))
        slew_thread.start()

    def _shutter_action(self, idx, seconds, after_shutter_state):
        self.mc_serial.enable_relay(idx, seconds)
        sleep(seconds)
        self.ns.shutter = after_shutter_state
        self.ns.slewing = False


    def find_home(self):
        # TODO
        # slew to home position
        # init home position to default home position
        # at home is now true
        logging.error("Find home not implemented yet")
        return

    def set_home_azimuth(self, home_az):
        self._update_azimuth()
        self.dome_calc.update_params(self.dome_calc.park_pos, self.curr_pos, self.steps_per_turn, self.turns_per_rotation)
        self._save_settings()

    def park(self):
        self.slew_to_az(self.dome_calc.park_pos.az)

    # Returns the status of the dome shutter or roll-off roof. 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error
    def get_shutter_status(self):
        return self.ns.shutter

    def set_park_azimuth(self):
        self._update_azimuth()
        self.dome_calc.update_params(self.curr_pos, self.dome_calc.home_pos, self.steps_per_turn, self.turns_per_rotation)
        self._save_settings()

    def get_azimuth(self):
        if self.conformance:
            logging.warning("returning conformance (faked) azimuth")
            self.curr_pos = self.dome_calc.get_domepos_az(self.ns.target_az)
        else:
            self._update_azimuth()
        return self.curr_pos.az

    @synchronized_method
    @cachetools.func.ttl_cache(maxsize=1, ttl=0.1)
    def _update_azimuth(self):
        steps, check1 = self.mc_serial.get_steps()
        turns, check2 = self.mc_serial.get_turns()
        if check1 and check2:
            self.curr_pos = self.dome_calc.get_domepos(steps, turns)
            logging.debug(f"Dome updating azimuth: {steps=}, {turns=}, {self.curr_pos=}")
        else:
            logging.debug(f"Error in checksum: {steps=}, {check1=}, {turns=}, {check2=}")

    def _check_azimuth(self, target_az):
        """ Check that AZIMUTH is > 0 and < 360 """
        result = {}
        if (target_az < 0 or target_az > 360):
            result['OK'] = False
            result['ErrorMessage'] = "Target azimuth is < 0 or > 360"
            result['ErrorNumber'] = 1025
            return False, result
        return True, None

    def slew_to_az(self, target_az: float):
        """ Starts the thread that makes the dome slew to a target AZ """
        checkok, res = self._check_azimuth(target_az)
        if not checkok:
            return res
        self.ns.target_az = target_az
        # slewing could be due to shutter, not dome !!!
        if not self.ns.domeslewing:
            slew_thread = Thread(target=self._slew_to_az)
            slew_thread.start()
            logging.info("started thread")

    def _slew_to_az(self):
        self.ns.aborted = False
        self.ns.slewing = True
        self.ns.domeslewing = True
        ## get direction and distance
        rotation = self._slew_update(self.ns.target_az)
        logging.debug(f"Slewing to azimuth: {self.ns.target_az=}, {self.curr_pos.az=}")
        while(abs(rotation) > 0.5 and not self.ns.aborted):
            logging.info(f"Slewing, rotation is {rotation}, {self.ns.target_az=}, {self.curr_pos.az=}")
            ## enable relay in correct direction
            ## loop until distance < 0.5 degree OR takes too long
            self.mc_serial.enable_relay(RELAY_IDX, 10)
            sleep(1)
            diffold = diff
            _, diff = self._slew_update(self.ns.target_az)
            diffdiff = abs(diff - diffold)
            logging.info(f"After slewing, diff is {diff}, {self.ns.target_az=}, {self.curr_pos.az=} {RELAY_IDX=}, {self.ns.limitcounter=}")
        logging.info(f"Slew done, diff is {diff}")
        self.mc_serial.enable_relay(RELAY_IDX, 0) # stop dome slewing
        self.ns.slewing = False
        self.ns.domeslewing = False
        return {'OK': True}

    def _slew_update(self, target_az: float):
        old_pos = self.curr_pos
        current_az = self.get_azimuth() # also updates
        rotation = self.dome_calc.rotation_direction(current_az, target_az, self.LIMITS, self.ns.limitcounter)
        dir_sign = utils.direction_sign(direction) # either 1 or -1
        limitchange = dir_sign*abs(old_pos.az - current_az) if old_pos is not None else 0
        logging.info(f"Changing limitcounter with {limitchange} to {self.ns.limitcounter + limitchange}, {direction=}, {dir_sign=}, {old_pos.az=}, {current_az=}")
        self.ns.limitcounter = self.ns.limitcounter + limitchange
        return rotation

    def synctoazimuth(self, target_az: float):
        print(f"Synctoazimuth with curr az = {self.curr_pos.az}, target az = {target_az}")
        checkok, res = self._check_azimuth(target_az)
        if not checkok:
            return res
        self._update_azimuth()
        self.ns.slewing = True
        self.curr_pos = self.dome_calc.sync_on_position(self.curr_pos, target_az)
        # self.curr_az = target_az
        self.ns.slewing = False
        print(f"Synctoazimuth after: curr az = {self.curr_pos.az}, target az = {target_az}")
        return {'OK': True}

