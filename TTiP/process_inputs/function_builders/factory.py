"""
Contains a factory that can be used to generate FunctionBuilders based on their
filename.
"""

from importlib import import_module
from inspect import getmembers, isabstract, isclass

from TTiP.process_inputs.function_builders.base import FunctionBuilder


class FunctionBuilderFactory:
    """
    Provides the factory method for creating function builders.
    Any FunctionBuilder can be created from this using the filename provided it
    is in the current directory.
    """

    @staticmethod
    def create_function_builder(function_type):
        """
        Create a FunctionBuilder subclass instance from the associated
        filename.

        Args:
            function_type (string):
                The name for the type of function, this should match the
                filename that the class is stored in.

        Raises:
            RuntimeError: If no unique class is found for the given input.

        Returns:
            FunctionBuilder: Initialised FunctionBuilder subclass.
        """
        module = import_module('.' + function_type, __package__)

        classes = getmembers(
            module, lambda m: isclass(m)and not isabstract(m)
            and issubclass(m, FunctionBuilder)
            )

        if len(classes) != 1:
            raise RuntimeError('Could not get unique function builder.')

        return classes[0][1]()
