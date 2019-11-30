import sys
import traceback


def produce_exception():
    eg = traceback.format_exception(*sys.exc_info())
    error_message = ''
    cnt = 0
    for er in eg:
        cnt += 1
        # if not 'lib/python' in er and not 'lib\\' in er:
        error_message += er + '<br><br>'
    return error_message