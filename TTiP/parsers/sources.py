"""
This contains the parser for parsing the SOURCES section of the config.
"""
from TTiP.function_builders.factory import FunctionBuilderFactory


class SourcesParser:
    """
    A parser for the sources section of the config file.

    Attributes:
        source (Function):
            The sum of all the source terms.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Initializer for the SourcesParser class.
        """
        self.source = None

    def parse(self, conf):
        """
        Parse the SOURCES section of the config into the sources attribute.

        Args:
            conf (configparser section or dict):
                The full SOURCES section from the config.
        """
        sources = FunctionBuilderFactory.create_function_dict(conf)
        self.source = sum(sources.values())
