r"""
The Constant function creates a uniform function of `value` across the whole
domain.

The exact formula is:

.. math::

    \text{constant}(x, \text{value}) = \text{value}

Where:

- value is a scalar
"""
from firedrake import Constant

from TTiP.function_builders.function_builder import FunctionBuilder


class ConstantBuilder(FunctionBuilder):
    """
    A FunctionBuilder to create a constant valued function.

    Required Properties:
        value (int, float):
            This is the value that the constant will have.
    """
    # pylint: disable=too-few-public-methods
    properties = {'value': (int, float)}

    def build(self):
        """
        Build the constant valued firedrake function.

        Raises:
            AttributeError: If required properties are not defined.

        Returns:
            Function: firedrake Constant set to te given value.
        """
        value = self._props['value']
        if value is None:
            raise AttributeError('"value" has not been defined.')

        return Constant(value)
