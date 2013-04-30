# coding=utf-8
import yaml

from system.logging import *

def load_file(filename):
    try:
        fh = open(filename, "r")
        data = fh.read()
        fh.close()

        return yaml.load(data)
    except Exception as e:
        handle_debug_error()
        error("Problem loading configuration from file: %s" % filename)
        error("%s" % e)
        return None

def save_file(filename, dictionary):
    try:
        fh = open(filename, "w")
        data = yaml.dump(dictionary)
        fh.write(data)
        fh.flush()
        fh.close()

        return True
    except Exception as e:
        handle_debug_error()
        error("Problem saving configuration to file: %s" % filename)
        error("%s" % e)
        return False