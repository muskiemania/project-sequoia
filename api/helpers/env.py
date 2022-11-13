import os

class EnvConfig:

    def __init__(self):
        pass

    @property
    def name(self):
        return os.getenv('ENV')
