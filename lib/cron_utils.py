import datetime
import logging
from crontab import CronTab

import settings

def is_executable(value):
    ct = CronTab(value)
    if ct.previous() > -settings.JOB_CHECK_PERIOD:
        return True
    else:
        return False
