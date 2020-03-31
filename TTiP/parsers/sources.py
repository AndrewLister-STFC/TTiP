"""
This contains the parser for parsing the SOURCES section of the config.
"""
from TTiP.parsers.base import FunctionSectionParser


class SourcesParser(FunctionSectionParser):
    """
    A parser for the sources section of the config file.

    Attributes:
        source (Function):
            The sum of all the source terms.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, mesh, V):
        """
        Initializer for the SourcesParser class.

        Args:
            mesh (Mesh):
                The mesh that the functions should be interpolated over.
            V (FunctionSpace):
                The function space that the functions should belong to.
        """
        super().__init__(mesh, V)
        self.source = None

    def parse(self, conf):
        """
        Parse the SOURCES section of the config into the sources attribute.

        Args:
            conf (configparser section or dict):
                The full SOURCES section from the config.
        """
        sources = self.factory.create_function_dict(conf)
        self.source = sum(sources.values())
