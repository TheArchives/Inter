# coding=utf-8
import time
import traceback
import sys

DEBUG = True

BASE_STRING = "%s | %s | %s"
LOG_STRING = "%s\n"
RJUST_LENGTH = 5

def _log(out):
    fh = open("output.log", "a")
    fh.write(LOG_STRING % out)
    fh.flush()
    fh.close()

def _output_string(level, data):
    if not "\n" in data:
        data += "\n"
    for line in data.split("\n"):
        if len(line) > 0:
            now = time.strftime("%d %b - %H:%M:%S", time.localtime())
            out = BASE_STRING % (now, level.rjust(RJUST_LENGTH), line)
            _log(out)
            print out
def _space(data):
    _output_string("", data)

def info(data):
    _output_string("INFO", data)

def warn(data):
    _output_string("WARN", data)

def error(data):
    _output_string("ERROR", data)

def debug(data):
    if DEBUG:
        _output_string("DEBUG", data)

def handle_debug_error():
    if DEBUG:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        data = traceback.format_exception(exc_type, exc_value, exc_traceback)
        debug("\n".join(data))