"""
This contains the parser for parsing the PARAMETERS section of the config.
"""
from TTiP.function_builders.factory import FunctionBuilderFactory


class ParametersParser:
    """
    A parser for the parameters section of the config file.

    Attributes:
        density (Function):
            The sum of all the function specified for density.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Initializer for the ParametersParser class.
        """
        self.density = None

    def parse(self, conf):
        """
        Parse the PARAMETERS section of the config into the various attributes.

        Args:
            conf (configparser section or dict):
                The full PARAMETERS section from the config.
        """
        all_functions = FunctionBuilderFactory.create_function_dict(conf)
        self.density = all_functions['density']
