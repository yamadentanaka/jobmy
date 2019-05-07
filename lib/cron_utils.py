import datetime
import logging

from lib import string_utils

class ExecutableChecker:
    def __init__(self, value, last_exec_time):
        self.value = value
        self.last_exec_time = last_exec_time
        if self.is_valid_format():
            self.invalid_format = False
            self._set_params()
        else:
            self.invalid_format = True

    def _warning(self):
        logging.warning("invalid schedule format. [%s]".format(self.value))

    def _set_params(self):
        ary = self.value.split(" ")
        self.minute = ary[0]
        self.hour = ary[1]
        self.day = ary[2]
        self.month = ary[3]
        self.dotw = ary[4] # day of the week (0=Sun,1=Mon,2=Tue,3=Wed,4=Thu,5=Fri,6=Sat,7=Sun)

    def _get_interval_value(self, value):
        return value.replace('*/', '')

    def _is_interval(self, value):
        return '*/' in value

    def _is_valid_param(self, param):
        if param == '*':
            return True
        elif '*/' in param:
            param_interval = self._get_interval_value(param)
            if string_utils.is_int(param_interval):
                return True
            else:
                return False
        else:
            return string_utils.is_int(param)

    def is_valid_format(self):
        ary = self.value.split(" ")
        if len(ary) != 5:
            self._warning()
            return False
        else:
            interval_count = 0
            minute = ary[0]
            if not self._is_valid_param(minute):
                self._warning()
                return False
            if self._is_interval(minute):
                interval_count += 1
            hour = ary[1]
            if not self._is_valid_param(hour):
                self._warning()
                return False
            if self._is_interval(hour):
                interval_count += 1
            day = ary[2]
            if not self._is_valid_param(day):
                self._warning()
                return False
            if self._is_interval(day):
                interval_count += 1
            month = ary[3]
            if not self._is_valid_param(month):
                self._warning()
                return False
            if self._is_interval(month):
                interval_count += 1
            dotw = ary[4]
            if not self._is_valid_param(dotw):
                self._warning()
                return False
            if self._is_interval(dotw):
                interval_count += 1
            # interval is only one setting.
            if interval_count > 1:
                self._warning()
                return False
            return True

    def is_executable(self):
        if self.invalid_format:
            return False
        # minute
        if '*/' in self.minute:
            minute_interval = int(self._get_interval_value(self.minute))
            cur_time = datetime.now()
            diff = cur_time - last_exec_time
            if int(diff.total_seconds() / 60) >= minute_interval:
                return True
            else:
                return False
        elif '*' != self.minute and int(self.minute) > 59:
            self._warning()
            return False
        # hour
        if '*/' in self.hour:
            if self.minute != '*':
                self._warning()
                return False
            hour_interval = int(self._get_interval_value(self.hour))
            cur_time = datetime.now()
            diff = cur_time - last_exec_time
            if int(diff.total_seconds() / (60 * 60)) >= hour_interval:
                return True
            else:
                return False
        # day
        # month
        # day of the week
        return True
