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
        self._start: float = 0.0
        self._end: float = 0.0
        self._stored: float = 0.0
    # Start the timer
    def start(self):
        self._start = time.perf_counter()
    # Stop the timer
    def stop(self):
        self._end = time.perf_counter()
    # Get the time recorded (in sec) from start and stop
    # Return: float
    def get_time(self):
        return self._end - self._start

# Get the time offset by seconds
# Return: datetime
def get_time_offset(sec: float):
    return datetime.datetime.now() + datetime.timedelta(seconds=sec)

# Get the time left (in seconds) until a certain datetime
# Return: int
def get_seconds_until(dt: datetime):
    return (dt - datetime.datetime.now()).seconds

# Get the exact time left until a certain datetime
# Return: str
def get_time_until(dt: datetime):
    td = (dt - datetime.datetime.now())
    hours, remainder = divmod(int(td.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    if td.days > 0:
        return str(td.days) + "d " + str(hours) + "h " + \
            str(minutes) + "m " + str(seconds) + "s"
    elif hours > 0:
        return str(hours) + "h " + str(minutes) + "m " + str(seconds) + "s"
    elif minutes > 0:
        return str(minutes) + "m " + str(seconds) + "s"
    else:
        return str(seconds) + "s"

# Get number returned as at least two decimal places
# Return: str
def _str(num: int):
    return ("-" if num < 0 else "") + (str(0) if abs(num) < 10 else "") + str(abs(num))

# Convert time in seconds to timestamp (h:m:s)
# Return: str
def get_timestampstr(sec: int):
    hours, remainder = divmod(sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    if hours > 0:
        return _str(hours)+":"+_str(minutes)+":"+_str(seconds)
    else:
        return _str(minutes)+":"+_str(seconds)
    
# Convert time in seconds to readable time (h, m, s)
# Return: str
def get_timestr(sec: int):
    hours, remainder = divmod(sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)

    if hours > 0:
        return str(hours)+"h "+str(minutes)+"m "+str(seconds)+"s"
    elif minutes > 0:
        return str(minutes)+"m "+str(seconds)+"s"
    else:
        return str(seconds)+"s"
    