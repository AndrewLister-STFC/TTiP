"""
This class holds the abstract base class for all FunctionBuilders.
A FunctionBuilder is a class that will take properties such as scalars and
weights, and build a function that can be used by firedrake.

FunctionBuilders must define:
    properties (dict):
        This should contain all properties and the expected type(s).
        e.g. {'alpha': string, 'beta': (int, float)}
    build (function):
        This should take no arguments and return a firedrake Function-like
        object.
"""
from abc import ABC


class FunctionBuilder(ABC):
    """
    Abstract base class for FunctiionBuilders which are used to build firedrake
    Functions given properties.

    To create a FunctionBuilder, inherit from this class and override:
        properties (dict):
            This should have property names and types as the keys and values
            respectively.
        build (function):
            Take no arguments and return a firedrake Function.

    Attributes:
        _props (dict):
            Dynamic storage for the values of the properties.
    """

    properties = {}

    def __init__(self):
        """
        Initialiser for the FunctionBuilder base class.
        """
        self._props = {k: None for k in self.properties}

    def assign(self, name, value):
        """
        Assign a value to a property by name.
        Checks that property is valid on the FunctionBuilder, and checks the
        type is compatible.

        Args:
            name (string): [description]
            value ([type]): [description]

        Raises:
            TypeError: [description]
            KeyError: [description]
        """
        if name in self.properties:
            if isinstance(value, self.properties[name]):
                self._props[name] = value
            else:
                raise TypeError('Property {} must be of type: {}, not {}.'
                                ''.format(name, self.properties[name],
                                          type(value)))
        else:
            raise KeyError('Property "{}" is not valid with this function.'
                           ''.format(name))

    def build(self):
        """
        Return the Function that can be used by firedrake.

        Returns:
            Function: The complete firedrake Function.
        """
        raise NotImplementedError('This is an abstract class.')
