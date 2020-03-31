"""
This contains the parser for parsing the SOLVER section of the config.
"""
from TTiP.parsers.parse_args import process_arg
from TTiP.parsers.base import SectionParser


class SolverParser(SectionParser):
    """
    A parser for the solver section of the config file.

    Attributes:
        file_path (string):
            The location to save the output to.
        method (string):
            The method to use for the solve.
        params (dict):
            Any parameters for the selected method.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Initializer for the SolverParser class.
        """
        super().__init__()
        self.file_path = None
        self.method = None
        self.params = {}

    def parse(self, conf):
        """
        Parse the SOLVER section of the config into the required attributes.

        Args:
            conf (configparser section or dict):
                The full SOLVER section from the config.
        """
        self.file_path = conf['file_path']
        self.method = conf['method']
        self.params = {k: process_arg(v) for k, v in conf.items()
                       if k not in ['file_path', 'method']}
