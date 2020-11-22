import configparser

class ConfigHelpers

    def __init__(self, filename):
        self._filename = filename
        self._config = None

    def init(self):
        self._config = configparser.ConfigParser()
        self._config.read(self._filename)

    def get_config(self):
        return self._config

