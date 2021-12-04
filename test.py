import datetime
import tzlocal

def make_time_str(format:str=None):
    time = datetime.datetime.now()
    if format is not None:
        return time.strftime(format)
    return time.strftime("%d.%m.%Y %H:%M:%S")
make_time_str()