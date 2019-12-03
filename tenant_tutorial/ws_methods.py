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


def replace_key_in_list(values, old_key, new_key):
    for obj in values:
        obj[new_key] = obj.pop(old_key)