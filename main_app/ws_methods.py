import sys
import traceback
from datetime import datetime
from datetime import timedelta


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    error_message = ''
    cnt = 0
    for er in eg:
        cnt += 1
        if not 'lib/python' in er and not 'lib\\' in er:
            error_message += er + '<br><br>'
    return error_message

def add_interval(interval_type, inc, dt=None):
    inc = int(inc)
    if not dt:
        dt = datetime.now()
    if interval_type == 'years':
        dt = dt + timedelta(years=inc)
    if interval_type == 'months':
        dt = dt + timedelta(months=inc)
    if interval_type == 'days':
        dt = dt + timedelta(days=inc)
    if interval_type == 'hours':
        dt = dt + timedelta(hours=inc)
    if interval_type == 'minutes':
        dt = dt + timedelta(minutes=inc)
    if interval_type == 'seconds':
        dt = dt + timedelta(seconds=inc)
    return dt
