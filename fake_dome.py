import time

class FakeDome:
    connected = False
    # 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error
    shutter = 1
    slewing = False
    slaved = False
    park_az = 0
    park_alt = 0
    curr_alt = 0
    curr_az = 0
    home_az = 180
    park_az = 90

    # get azimuth and check if it's near the home position (less than 1 degree)
    def is_at_home(self):
        return abs(self.curr_az - self.home_az) < 1

    # get azimuth and check if it's near the home position (less than 1 degree)
    def is_at_park(self):
        return abs(self.curr_az - self.park_az) < 1

    def close_shutter(self):
        self.shutter = 3
        time.sleep(1)
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
        self.curr_az = self.home_az

    def park(self):
        self.slew_to_az(self.park_az)

    # Returns the status of the dome shutter or roll-off roof. 0 = Open, 1 = Closed, 2 = Opening, 3 = Closing, 4 = Shutter status error
    def get_shutter_status(self):
        return self.shutter

    def set_park_azimuth(self):
        self.park_az = self.curr_az


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

