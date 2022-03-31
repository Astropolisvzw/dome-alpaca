import threading
from enum import Enum
import math

class Relay(Enum):
    UP_IDX= 0
    DOWN_IDX=1
    LEFT_IDX=2
    RIGHT_IDX=3

# synchronized methods taken from https://www.theorangeduck.com/page/synchronized-python

def synchronized(func):

    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


def synchronized_method(method):

    outer_lock = threading.Lock()
    lock_name = "__"+method.__name__+"_lock"+"__"

    def sync_method(self, *args, **kws):
        with outer_lock:
            if not hasattr(self, lock_name): setattr(self, lock_name, threading.Lock())
            lock = getattr(self, lock_name)
            with lock:
                return method(self, *args, **kws)

    return sync_method

def best_rotation(origin, target):
    """ Given an origin angle and target angle (0-360 degrees), return the smallest rotation and direction to go from origin to target """
    MAX_VALUE=360.0
    signedDiff = 0.0;
    raw_diff = origin - target if origin > target else target - origin
    mod_diff = math.fmod(raw_diff, MAX_VALUE);

    if(mod_diff > (MAX_VALUE/2) ):
        # There is a shorter path in opposite direction
        signedDiff = (MAX_VALUE - mod_diff)
        if(target>origin): signedDiff = signedDiff * -1;
    else:
        signedDiff = mod_diff;
        if(origin>target): signedDiff = signedDiff * -1;

    return signedDiff;

def rotation_to_direction(rotation):
    if rotation < 0:
        return Relay.LEFT_IDX
    return Relay.RIGHT_IDX    

def direction_sign(self, direction:Relay):
    """ Given a relay direction, return the other direction """
    if direction == Relay.LEFT_IDX:
        return -1
    return 1

def direction_invert(self, direction:Relay):
    """ Given a relay direction, return the other direction """
    if direction == Relay.LEFT_IDX:
        return Relay.RIGHT_IDX
    return Relay.LEFT_IDX

