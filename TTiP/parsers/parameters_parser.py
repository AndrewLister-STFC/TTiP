"""
This contains the parser for parsing the PARAMETERS section of the config.
"""
from firedrake import Constant

from TTiP.parsers.parser import FunctionSectionParser


class ParametersParser(FunctionSectionParser):
    """
    A parser for the parameters section of the config file.

    Attributes:
        density (Function):
            The value specified for density.
        coulomb_ln (Function):
            The value specified for the coulomb_ln.
        z (Function):
            The value specified for Z.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, mesh, V):
        """
        Initializer for the ParametersParser class.

        Args:
            mesh (Mesh):
                The mesh that the functions should be interpolated over.
            V (FunctionSpace):
                The function space that the functions should belong to.
        """
        super().__init__(mesh, V)
        self.parameters = {'electron_density': Constant(5.0e28),
                           'coulomb_ln': Constant(10),
                           'z': Constant(12)}

    def parse(self, conf):
        """
        Parse the PARAMETERS section of the config into the various attributes.

        Args:
            conf (configparser section or dict):
                The full PARAMETERS section from the config.
        """
        all_functions = self.factory.create_function_dict(conf)
        self.parameters.update(all_functions)
