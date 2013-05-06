# coding=utf-8
import os
import yaml
import logging
import system.util as util

from system.decorators import Singleton

BASE_PATH = "data/%s"


@Singleton
class storage(object):
    """
    Storage - A singleton for working with data storage.

    Use the data() function at the bottom of this file or storage.Instance() to get an instance of this.

    Remember, this is NOT for configuration. Use the configuration class in conf for this.
    Data storage is for data the user should never normally have to modify by hand. If you think they will, please
        consider using `system.config` instead.

    Public methods:
        load_file()
        save_file()
    """
    files = {}
    logger = logging.getLogger("Storage")

    def __init__(self):
        pass

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
        This will only save stuff in the data/ folder, don't specify data/ in the path.
        :param dictionary: The data to be saved, a standard Python dictionary
        :param filename:   The file to save to, without data/
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

    def load_file(self, filename):
        """
        Load a dictionary from a yaml file.
        This will only load stuff in the data/ folder, don't specify data/ in the path.
        :param filename: The file to load from, without data/
        """
        if "\\" in filename:
            filename = filename.replace("\\", "/")
        if "/" in filename:
            filename = filename.replace("../", "")
        return self._load_file(BASE_PATH % filename)


def data():
    """
    Convenience method for getting an instance of the configuration singleton.
    """
    return storage.Instance()