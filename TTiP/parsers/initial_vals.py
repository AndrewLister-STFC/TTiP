"""
This contains the parser for parsing the INITALVALUE section of the config.
"""
from TTiP.function_builders.factory import FunctionBuilderFactory


class InitialValParser:
    """
    A parser for the initial value section of the config file.

    Attributes:
        initial_val (Function):
            The sum of all the initial value terms.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Initializer for the InitialValParser class.
        """
        self.initial_val = None

    def parse(self, conf):
        """
        Parse the INITIALVALUE section of the config into the initial_val
        attribute.

        Args:
            conf (configparser section or dict):
                The full INITIALVALUE section from the config.
        """
        init_vals = FunctionBuilderFactory.create_function_dict(conf)
        self.initial_val = sum(init_vals.values())
