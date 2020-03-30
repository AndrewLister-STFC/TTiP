"""
This contains the parser for parsing the BOUNDARIES section of the config.
"""


class BoundaryCondsParser:
    """
    A parser for the boundaries section of the config file.

    Attributes:
        bcs (list<dict>):
            A list of the boundary conditions.
    """
    def __init__(self):
        """
        Initializer for the BoundaryCondsParser class.
        """
        self.bcs = None

    def parse(self, conf):
        """
        Parse the BOUNDARIES section of the config into the various attributes.

        Args:
            conf (configparser section or dict):
                The full BOUNDARIES section from the config.
        """
        pass
