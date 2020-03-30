"""
This contains the parser for parsing the BOUNDARIES section of the config.
"""
from TTiP.process_inputs.function_builders.factory import \
    FunctionBuilderFactory
from TTiP.utils.parse_args import process_arg


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
        Parse the BOUNDARIES section of the config into the bcs list.

        Args:
            conf (configparser section or dict):
                The full BOUNDARIES section from the config.
        """
        boundaries = {}
        for k, v in conf.items():
            names = k.lower().split('.')

            tmp_dict = boundaries
            for name in names[:-1]:
                if name not in tmp_dict:
                    tmp_dict[name] = {}
                tmp_dict = tmp_dict[name]

            tmp_dict[name[-1]] = process_arg(v)

        for b in boundaries.values():
            for k, v in b.items():
                if isinstance(v, dict) and 'type' in v:
                    f_type = v.pop('type')
                    func = FunctionBuilderFactory.create_function(f_type, **v)
                    boundaries[k] = func

        self.bcs = list(boundaries.values())
