r"""
The File function creates an function interpolated from data in a file.

The file must be a csv (optionally with a header row),
where the first n columns represent the coords and the final column
is the value at the coordinate.

e.g. For a 2D problem::

    x, y, val
    0.0, 0.0, 10.0
    0.1, 0.0, 9.0
    0.2, 0.0, 8.0
    0.3, 0.0, 7.0
    ...

Linear interpolation is used.
"""
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
        value = self._props['path']
        if value is None:
            raise AttributeError('"path" has not been defined.')
