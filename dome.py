from arduino_serial import ArduinoSerial
from configparser import ConfigParser
import logging
from dome_calc import DomeCalc
from dome_calc import DomePos
import os

class Dome:
    connected = False
    # 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error
    shutter = 1
    slewing = False
    slaved = False
    curr_pos: DomePos = None
    serial_port: str = None
    serial_baud: int = None
    mc_serial: ArduinoSerial = None
    dome_calc = DomeCalc()
    config_file: str = ''

    def __init__(self, config_file='ap_ashdome_config.ini'):
        self.config_file = config_file
        park_pos, home_pos, spt, tpr, serial_port, serial_baud = self.load_settings()
        self.dome_calc.update_params(park_pos, home_pos, spt, tpr)
        self.serial_port = serial_port
        self.serial_baud = serial_baud
        self.set_serial_port(self.serial_port, self.serial_baud)
        self.park_pos = park_pos
        self.home_pos = home_pos
        self.steps_per_turn = spt
        self.turns_per_rotation = tpr
        logging.info(f"Inited dome with park: {self.dome_calc.park_pos}, home: {self.dome_calc.home_pos}, spt: {spt}, tpr: {tpr}, serial port: {serial_port}")

    def set_serial_port(self, serial_port, serial_baud):
        if self.mc_serial is not None:
            self.mc_serial.close()
        self.serial_port = serial_port
        self.mc_serial = ArduinoSerial(self.serial_port, self.serial_baud)
        self.save_settings(self.dome_calc.park_pos, self.dome_calc.home_pos, self.steps_per_turn, self.turns_per_rotation, self.serial_port, self.serial_baud)

    def save_settings(self, park_pos, home_pos, spt, tpr, serial_port, serial_baud):
        config = ConfigParser()
        config.read(self.config_file)
        section = 'domeparams'
        config.add_section(section)
        config.set(section, 'park_az', str(park_pos.az))
        config.set(section, 'park_steps', str(park_pos.steps))
        config.set(section, 'park_turns', str(park_pos.turns))
        config.set(section, 'home_az', str(home_pos.az))
        config.set(section, 'home_steps', str(home_pos.steps))
        config.set(section, 'home_turns', str(home_pos.turns))
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
        park_az = config.getint(section, 'park_az')
        park_steps = config.getint(section, 'park_steps')
        park_turns = config.getint(section, 'park_turns')
        home_az = config.getint(section, 'home_az')
        home_steps = config.getint(section, 'home_steps')
        home_turns = config.getint(section, 'home_turns')
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

    def close_shutter(self):
        self.shutter = 3
        self.shutter = 1

    def abort_slew(self):
        return False

    def open_shutter(self):
        self.shutter = 2
        self.shutter = 0

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
        self.save_settings(self.dome_calc.park_pos, self.curr_pos, self.steps_per_turn, self.turns_per_rotation, self.serial_port)


    def park(self):
        self.slew_to_az(self.dome_calc.park_pos.az)

    # Returns the status of the dome shutter or roll-off roof. 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error
    def get_shutter_status(self):
        return self.shutter

    def set_park_azimuth(self):
        self._update_azimuth()
        self.dome_calc.update_params(self.curr_pos, self.dome_calc.home_pos, self.steps_per_turn, self.turns_per_rotation)
        self.save_settings(self.curr_pos, self.dome_calc.home_pos, self.steps_per_turn, self.turns_per_rotation, self.serial_port)

    def get_azimuth(self):
        self._update_azimuth()
        return self.curr_pos.az


    def _update_azimuth(self):
        steps, check1 = self.mc_serial.get_steps()
        turns, check2 = self.mc_serial.get_turns()
        if check1 and check2:
            self.curr_pos = self.dome_calc.steps_turn_to_az(steps, turns)
            logging.debug(f"Dome updating azimuth: {steps=}, {turns=}, {self.curr_pos=}")
        else:
            logging.debug(f"Error in checksum: {steps=}, {check1=}, {turns=}, {check2=}")

    def _check_azimuth(self, target_az):
        result = {}
        if (target_az < 0 or target_az > 360):
            result['OK'] = False
            result['ErrorMessage'] = "Target azimuth is < 0 or > 360"
            result['ErrorNumber'] = 1025
            return False, result
        return True, None

    def slew_to_az(self, target_az: float):
        checkok, res = self._check_azimuth(target_az)
        if not checkok:
            return res
        # TODO: DO SOMETHING REAL
        self.slewing = True
        self.curr_az = target_az
        self.slewing = False
        return {'OK': True}

    def synctoazimuth(self, target_az: float):
        #print(f"Getting synctoazimuth with curr az = {self.curr_az}, target az = {target_az}")
        checkok, res = self._check_azimuth(target_az)
        if not checkok:
            return res
        # TODO: DO SOMETHING REAL
        self.slewing = True
        self.curr_az = target_az
        self.slewing = False
        #print(f"synctoazimuth after: curr az = {self.curr_az}, target az = {target_az}")
        return {'OK': True}

