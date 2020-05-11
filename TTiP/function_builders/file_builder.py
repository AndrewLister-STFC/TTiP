r"""
The File function creates an function interpolated from data in a file.

The file must be a csv (optionally with a commented header row),
where the first n columns represent the coords and the final column
is the value at the coordinate.

e.g. For a 2D problem::

    # x, y, val
    0.0, 0.0, 10.0
    0.1, 0.0, 9.0
    0.2, 0.0, 8.0
    0.3, 0.0, 7.0
    ...

Cubic interpolation is used for 1-D or 2-D problems, while
linear interpolation is used for higher dimensional problems.
"""
import os

from firedrake import Function, VectorFunctionSpace, interpolate
from numpy import loadtxt
from scipy.interpolate import griddata

from TTiP.function_builders.function_builder import FunctionBuilder


class FileBuilder(FunctionBuilder):
    """
    A FunctionBuilder to create a function by interpolating over data from a
    file.

    Required Properties:
        path (str):
            This is the file that will be used.
    """
    # pylint: disable=too-few-public-methods
    properties = {'path': (str)}

    def build(self):
        """
        Build the interpolated firedrake function.

        Raises:
            AttributeError: If required properties are not defined.

        Returns:
            Function: firedrake Function with values from the file.
        """
        path = self._props['path']
        if path is None:
            raise AttributeError('"path" has not been defined.')

        if not os.path.exists(path):
            raise ValueError('Invalid path')

        data = loadtxt(path, delimiter=',')

        coords = data[:, :-1]
        vals = data[:, -1]

        # Now make the VectorFunctionSpace corresponding to V.
        W = VectorFunctionSpace(self.mesh, self.V.ufl_element())
        X = interpolate(self.mesh.coordinates, W)
        f = Function(self.V)

        method = 'linear' if coords.shape[1] > 2 else 'cubic'
        # Use the external data function to interpolate the values of f.
        f.dat.data[:] = griddata(coords, vals, X.dat.data, method)

        return f
