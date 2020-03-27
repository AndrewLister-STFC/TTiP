"""
This holds all functions related to parsing the TIME section of the config file
"""


class TimeParser:
    """
    A parser for the time section of the config file.

    Attributes:
        steps (int):
            The instantiated number of steps for time iteration.
        dt (float):
            The value for dt (change in time)
        max_t (float):
            The time to iterate until.
    """
    def __init__(self):
        """
        Initialiser for the TimeParser class.
        """
        self.steps = None
        self.dt = None
        self.max_t = None

    def parse(self, conf):
        """
        Parse the given config section into the relevent time values.

        Args:
            conf (configparser section):
                The config section for the time values.
        """
        if 'steps' in conf:
            self.steps = conf.getint('steps')

        if 'dt' in conf:
            self.dt = conf.getfloat('dt')

        if 'max_t' in conf:
            self.max_t = conf.getfloat('max_t')
