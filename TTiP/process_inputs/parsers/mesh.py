"""
This holds all functions related to parsing the MESH section of the config file
"""
import firedrake


class MeshParser:
    """
    A parser for the mesh section of the config file.

    Attributes:
        mesh (Mesh):
            This variable holds the instantiated mesh once it has been
            generated.
    """

    def __init__(self):
        """
        Initialiser for the MeshParser class.
        """
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

        mesh_type = conf.get('type')
        conf.pop('type')
        if mesh_type.lower() == 'file':
            mesh_type = 'Mesh'

        if not mesh_type.endswith('Mesh'):
            mesh_type += 'Mesh'

        mesh_cls = getattr(firedrake, mesh_type)

        processed_args = []
        args = conf.get('params')
        conf.pop('params')
        if args is not None:
            args = args.split(',')
            for arg in args:
                arg = self._process_arg(arg)
                processed_args.append(arg)

        kwargs = {}
        for k, v in conf.items():
            kwargs[k] = self._process_arg(v)

        self.mesh = mesh_cls(*processed_args, **kwargs)

    @staticmethod
    def _process_arg(val):
        """
        Convert a string into the correct value.
        e.g. "2" -> 2 (int)
             "false" -> False (bool)
             "1.8" -> 1.8 (float)
        
        Args:
            val (string): The value to convert.
        
        Returns:
            (bool, int, float, string): The converted value.
        """
        val = val.strip()
        if val.lower() == 'true':
            return True
        if val.lower() == 'false':
            return False

        try:
            val = int(val)
            return val
        except ValueError:
            pass

        try:
            val = float(arg)
            return val
        except ValueError:
            pass

        return val
