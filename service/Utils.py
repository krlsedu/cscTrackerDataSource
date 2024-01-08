import os
import pytz
from datetime import datetime


class Utils:
    def __init__(self):
        super().__init__()

    def work_time(self):
        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        h = h - 3
        return 8 <= h <= 19

    def work_day(self):
        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, min, sec, wd, yd, i = t
        return wd < 5

    def read_file(self, file_name):
        file_dir = os.path.dirname(os.path.realpath('__file__'))
        file_name = os.path.join(file_dir, file_name)
        file_handle = open(file_name)
        content = file_handle.read()
        file_handle.close()
        return content

    @staticmethod
    def get_format_date_time_in_tz(dt_string, format, original_tz='America/Sao_Paulo', new_tz='UTC'):
        dt_obj = datetime.strptime(dt_string, format)

        original_tz_ = pytz.timezone(original_tz)
        dt_obj = original_tz_.localize(dt_obj)

        new_tz_ = pytz.timezone(new_tz)
        new_dt_obj = dt_obj.astimezone(new_tz_)

        return new_dt_obj.strftime(format)
