# coding=utf-8
import os
import sys

import system.config as conf
import system.core as core
import system.logging as log

VERSION = "0.0.1"

created_files = []
created_folders = []

passed = 0
failed = 0

class null_stream:
    def write(self, text):
        pass

def no_output(func, *args):
    stdobak = sys.stdout
    null_instance = null_stream()
    sys.stdout = null_instance
    try:
        return func(*args)
    finally:
        sys.stdout = stdobak

def mv(old, new):
    try:
        os.rename(old, new)
    except:
        log.error("Error renaming %s to %s" % (old, new))
        log.handle_debug_error()
    else:
        log.info("Renamed %s to %s" % (old, new))

def silent_mv(old, new):
    try:
        os.rename(old, new)
    except:
        pass

def silent_rm(path):
    try:
        os.remove(path)
    except:
        try:
            os.removedirs(path)
        except:
            pass
    else:
        pass

def mkdir(path):
    try:
        os.mkdir(path)
    except:
        log.error("Error creating directory: " + path)
        log.handle_debug_error()
    else:
        created_folders.append(path)
        log.info("Created directory: " + path)

def mkfile(name, data=None):
    try:
        fh = open(name, "w")
        if data:
            fh.write(data)
            log.info("Created file with %s bytes of data: %s" % (len(data), name))
        else:
            log.info("Created empty file: %s" % name)
        fh.flush()
        fh.close()
    except:
        log.handle_debug_error()
        log.error("Error creating file: " + name)
    else:
        created_files.append(name)

def cleanup():
    created_files.reverse()
    created_folders.reverse()

    for filename in created_files:
        try:
            os.remove(filename)
        except:
            log.info("Error deleting file: " + filename)
            log.handle_debug_error()
        else:
            log.info("Deleted file: " + filename)

    for folder in created_folders:
        try:
            os.removedirs(folder)
        except:
            log.info("Error deleting directory: " + folder)
            log.handle_debug_error()
        else:
            log.info("Deleted directory: " + folder)

silent_mv("output.log", "output.log.bak")

log.info("Welcome to the test suite for Inter.")
log.info("This is test suite v%s" % VERSION)

log._space("==============================")

log.info("Creating test files...")
mkdir("test")
mkfile("test/config.yml", "test: OK")
log.info("Done creating test files.")

log._space("==============================")

log.info("This is an info message")
log.warn("This is a warning message")
log.error("This is an error message")
log.debug("This is a debug message")

log._space("==============================")

log.info("Testing configuration...")
indata = no_output(conf.load_file, "does-not-exist.yml")
if indata is None:
    passed += 1
    log.info("Passed | Loading non-existant config returns None")
else:
    failed += 1
    log.warn("Failed | Loading non-existant config returns None")
    log.warn("Returned data: %s" % indata)

indata = no_output(conf.load_file, "test/config.yml")
if indata == {"test": "OK"}:
    passed += 1
    log.info("Passed | Loading existing config returns correct data")
else:
    failed += 1
    log.warn("Failed | Loading existing config returns correct data")
    log.warn("Returned data: %s" % indata)

indata = no_output(conf.save_file, "test/gone/config.yml", {"test": "OK"})
if not indata:
    passed += 1
    log.info("Passed | Saving config in non-existant location returns False")
else:
    failed += 1
    log.warn("Failed | Saving config in non-existant location returns False")
    log.warn("Returned data: %s" % indata)

indata = no_output(conf.save_file, "test/config.yml", {"test": "OK"})
if indata:
    passed += 1
    log.info("Passed | Saving config over existing file returns True")
else:
    failed += 1
    log.warn("Failed | Saving config over existing file returns True")
    log.warn("Returned data: %s" % indata)

indata = no_output(conf.save_file, "test/new.yml", {"test": "OK"})
created_files.append("test/new.yml")
if indata:
    passed += 1
    log.info("Passed | Saving new config in existing location returns True")
else:
    failed += 1
    log.warn("Failed | Saving new config in existing location returns True")
    log.warn("Returned data: %s" % indata)

if os.path.exists("test/new.yml"):
    passed += 1
    log.info("Passed | New file is created when saving new config")
else:
    failed += 1
    log.warn("Failed | New file is created when saving new config")

log._space("==============================")

log.info("Cleaning up test files...")
cleanup()
log.info("Done cleaning up test files.")

log._space("==============================")

log.info("Results: %s passed, %s failed" % (passed, failed))

silent_rm("output.log")
silent_mv("output.log.bak", "output.log")