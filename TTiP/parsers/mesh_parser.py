"""
This holds all functions related to parsing the MESH section of the config file
"""
import firedrake
from TTiP.parsers.parse_args import Expression
from TTiP.parsers.parser import SectionParser


class MeshParser(SectionParser):
    """
    A parser for the mesh section of the config file.

    Attributes:
        mesh (Mesh):
            This variable holds the instantiated mesh once it has been
            generated.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Initialiser for the MeshParser class.
        """
        super().__init__()
        self.mesh = None

    def parse(self, conf):
        """
        Parse the given config section into an instantiated Mesh.

        Args:
            conf (configparser section):
                The config section for the mesh.

        Raises:
            AttributeError: If no mesh type is defined.
        """

        if 'type' not in conf:
            raise AttributeError('Must define a mesh type.')

        mesh_type = conf.pop('type')
        if mesh_type.lower() == 'file':
            mesh_type = 'Mesh'

        if not mesh_type.endswith('Mesh'):
            mesh_type += 'Mesh'

        mesh_cls = getattr(firedrake, mesh_type)

        element = conf.pop('element')
        order = conf.pop('order')
        try:
            order = int(order)
        except ValueError as e:
            raise TypeError from e

        processed_args = []
        args = conf.pop('params', None)
        if args is not None:
            args = Expression(args)
            processed_args = args.evaluate(None)

        kwargs = {}
        for k, v in conf.items():
            expr = Expression(v)
            kwargs[k] = expr.evaluate(None)

        self.mesh = mesh_cls(*processed_args, **kwargs)
        self.func_space = firedrake.FunctionSpace(self.mesh, element, order)
