# coding=utf-8
import os
import yaml
import logging
import system.util as util

from system.decorators import Singleton

BASE_PATH = "config/%s"


@Singleton
class configuration(object):
    """
    Configuration - A singleton for managing local configuration files and data.
    Don't directly create an instance of this; use configuration.Instance() instead!

    Please remember that configuration is not the same as data. Configuration is only for settings that should be
        editied by a user!

    This class will automatically load all configuration files specified in config/mapping.yml when instanciated.

    Public methods:
        get(key)                    Get configuration data for a given key, or False if it doesn't exist.
        save_file(filename, dict)   Save configuration to a file. If you do this a lot, consider using `system.storage`.
        save_mapping(key, filename) Save a mapping between a key and a filename.
        get_mapping(key)            Get a filename for a mapping, or None if it doesn't exist.
        reload()                    Reload all mappings and configurations.
    """
    files = {}
    logger = logging.getLogger("Config")

    def __init__(self):
        self.logger.info("Loading configuration into memory..")
        mappings = self._load_file(BASE_PATH % "mapping.yml")

        for n, f in mappings.items():
            data = self._load_file(BASE_PATH % f)
            if data:
                fmap = {"name": n, "path": f, "data": data}
                self.files[n] = fmap
                self.logger.info("Loaded configuration: '%s'" % n)
                self.logger.debug("Data: %s" % fmap)
            else:
                self.logger.info("Unable to load configuration: '%s'" % n)
        self.logger.info("Finished loading configuration.")

    def _load_file(self, filename):
        try:
            fh = open(filename, "r")
            data = fh.read()
            fh.close()

            return yaml.load(data)
        except Exception:
            util.output_exception(self.logger)
            return None

    def _save_file(self, filename, dictionary):
        try:
            fh = open(filename, "w")
            data = yaml.dump(dictionary, default_flow_style=False)
            fh.write(data)
            fh.flush()
            fh.close()

            return True
        except Exception:
            util.output_exception(self.logger)
            return False

    def save_file(self, filename, dictionary):
        """
        Save a dictionary to a yaml file.
        This will only save stuff in the config/ folder, don't specify config/ in the path.
        :param dictionary: The data to be saved, a standard Python dictionary
        :param filename:   The file to save to, without config/
        """
        if "\\" in filename:
            filename = filename.replace("\\", "/")
        if "/" in filename:
            filename = filename.replace("../", "")
            path = BASE_PATH % filename.split("/")
            path = path[0:len(path)-1]
            path = "/".join(path)
            if not os.path.exists(path):
                os.makedirs(path)
        self._save_file(BASE_PATH % filename, dictionary)


    def get(self, key):
        """
        Gets the configuration data for a given key, if it exists.
        If not, returns false.
        :param key: The key to get configuration for.
        :return:    The configuration data dict, or False.
        """
        if key in self.files:
            return self.files.get(key).get("data")
        return False

    def save_mapping(self, mapping, filename):
        """
        Save a new mapping or overwrite an old one.
        This does not check if the mapping already exists, your plugin should do that.
        :param mapping:  The key used to identify the mapping
        :param filename: The filename this mapping identifies (without config/)
        """
        self.logger.debug("Saving mapping: %s (%s)" % (mapping, filename))
        mappings = self._load_file(BASE_PATH % "mapping.yml")
        mappings[mapping] = filename
        self._save_file(BASE_PATH % "mapping.yml", mappings)

    def get_mapping(self, mapping):
        """
        Get the filename for an existing mapping, or None if it doesn't exist.
        :param mapping: The key used to identify the mapping
        """
        mappings = self._load_file(BASE_PATH % "mapping.yml")
        if mapping in mappings:
            return mappings[mapping]
        return None

    def reload(self):
        """
        Reloads the entire configuration set from the mappings.
        """
        self.logger.info("Reloading configuration..")
        mappings = self._load_file(BASE_PATH % "mapping.yml")

        self.files = {}

        for n, f in mappings.items():
            self.logger.info("Loading configuration: '%s'" % n)
            data = self._load_file(BASE_PATH % f)
            if data:
                fmap = {"name": n, "path": f, "data": data}
                self.files[n] = fmap
                self.logger.debug("Data: %s" % fmap)
        self.logger.info("Finished reloading configuration.")


def conf():
    """
    Convenience method for getting an instance of the configuration singleton.
    """
    return configuration.Instance()