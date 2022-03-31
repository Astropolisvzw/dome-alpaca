import threading
from enum import Enum

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

def smallest_diff(angle1, angle2):
    """ smallest diff between 2 angles, including sign (minus is LEFT rotate) """
    diff1 = (angle1 - angle2)%360
    diff2 = (angle2 - angle1)%360
    return min(diff1, diff2)

class Relay(Enum):
    UP_IDX= 0
    DOWN_IDX=1
    LEFT_IDX=2
    RIGHT_IDX=3
