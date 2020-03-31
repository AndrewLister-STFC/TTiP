"""
This contains the parser for parsing the INITALVALUE section of the config.
"""
from TTiP.parsers.base import FunctionSectionParser


class InitialValParser(FunctionSectionParser):
    """
    A parser for the initial value section of the config file.

    Attributes:
        initial_val (Function):
            The sum of all the initial value terms.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, mesh, V):
        """
        Initializer for the InitialValParser class.

        Args:
            mesh (Mesh):
                The mesh that the functions should be interpolated over.
            V (FunctionSpace):
                The function space that the functions should belong to.
        """
        super().__init__(mesh, V)
        self.initial_val = None

    def parse(self, conf):
        """
        Parse the INITIALVALUE section of the config into the initial_val
        attribute.

        Args:
            conf (configparser section or dict):
                The full INITIALVALUE section from the config.
        """
        init_vals = self.factory.create_function_dict(conf)
        self.initial_val = sum(init_vals.values())
