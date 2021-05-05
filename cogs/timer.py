import datetime
import time

#####################
#       timer       #
#####################
# Everything to do with time calculations
# Mostly helpful for debugging purposes

# Basic Timer class to measure function performance
class Timer:
    def __init__(self):
        self._start : float=0.0
        self._end : float=0.0
    

    # Start the timer
    def start(self):
        self._start = time.perf_counter()

    # Stop the timer
    def stop(self):
        self._end = time.perf_counter()

    # Get the time recorded (in sec) from start and stop
    # Returns: float
    def get_time(self):
        return self._end - self._start


# Get the time offset by seconds
# Return: datetime
def get_time_offset(sec: float=0.0):
    return datetime.datetime.now() + datetime.timedelta(seconds=sec)

# Get the time left until a certain datetime (in seconds)
# Return: int
def get_time_until(dt: datetime):
    return (dt - datetime.datetime.now()).seconds
