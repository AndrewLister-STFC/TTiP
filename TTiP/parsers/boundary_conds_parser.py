"""
This contains the parser for parsing the BOUNDARIES section of the config.
"""
from TTiP.parsers.parse_args import process_args
from TTiP.parsers.parser import FunctionSectionParser


class BoundaryCondsParser(FunctionSectionParser):
    """
    A parser for the boundaries section of the config file.

    Attributes:
        bcs (list<dict>):
            A list of the boundary conditions.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, mesh, V):
        """
        Initializer for the BoundaryCondsParser class.

        Args:
            mesh (Mesh):
                The mesh that the function will interpolate over.
            V (FunctionSpace):
                The function space that the function should belong to.
        """
        super().__init__(mesh, V)
        self.bcs = None

    def parse(self, conf):
        """
        Parse the BOUNDARIES section of the config into the bcs list.

        Args:
            conf (configparser section or dict):
                The full BOUNDARIES section from the config.
        """
        boundaries = process_args(conf,
                                  factory=self.factory,
                                  str_keys=['type', 'boundary_type'])

        for b in boundaries.values():
            for k, v in b.items():
                if isinstance(v, dict) and 'type' in v:
                    f_type = v.pop('type')
                    func = self.factory.create_function(f_type, **v)
                    b[k] = func

        self.bcs = list(boundaries.values())
