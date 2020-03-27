"""
This file holds the ConstantBuolder class which is used to build constant
valued funcions.
"""
from firedrake import Constant

from TTiP.process_inputs.function_builders.base import FunctionBuilder


class ConstantBuilder(FunctionBuilder):
    """
    A FunctionBuilder to create a constant valued function.

    Required Properties:
        value (int, float):
            This is the value that the constant will have.
    """
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
