"""
This contains the parser for parsing the PHYSICS section of the config.
"""
from TTiP.parsers.parser import SectionParser


class PhysicsParser(SectionParser):
    """
    A parser for the physics section of the config file.

    Attributes:
        limit_conductivity (bool):
            Whether to enable a lower bound on conductivity.
        limit_flux (bool):
            whether to enable flux_limiting.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Initializer for the PhysicsParser class.
        """
        super().__init__()
        self.limit_conductivity = None
        self.limit_flux = None

    def parse(self, conf):
        """
        Parse the PHYSICS section of the config into the required attributes.

        Args:
            conf (configparser section or dict):
                The full PHYSICS section from the config.
        """

        self.limit_conductivity = conf.getboolean('limit_conductivity')
        self.limit_flux = conf.getboolean('limit_flux')
