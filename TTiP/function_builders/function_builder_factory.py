"""
Contains a factory that can be used to generate FunctionBuilders based on their
filename.
"""

from importlib import import_module
from inspect import getmembers, isabstract, isclass

from TTiP.function_builders.function_builder import FunctionBuilder
from TTiP.parsers.parse_args import process_arg


class FunctionBuilderFactory:
    """
    Provides the factory method for creating function builders.
    Any FunctionBuilder can be created from this using the filename provided it
    is in the current directory.

    Also provdes a utility function to create the function given a list of
    properties.
    """
    def __init__(self, mesh, V):
        """
        Initialiser for the FunctionBuilderFactory

        Args:
            mesh (Mesh):
                The mesh that the function will interpolate over.
            V (FunctionSpace):
                The function space that the function should belong to.
        """
        self.mesh = mesh
        self.V = V

    def create_function_builder(self, function_type):
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
        name = function_type.lower() + '_builder'
        module = import_module('.' + name, __package__)

        classes = getmembers(
            module, lambda m: isclass(m) and not isabstract(m)
            and issubclass(m, FunctionBuilder)
            )

        if len(classes) != 1:
            raise RuntimeError('Could not get unique function builder for {}.'
                               ''.format(function_type))

        return classes[0][1](mesh=self.mesh, V=self.V)

    def create_function(self, function_type, **properties):
        """
        Create a fully initialised function and return it.

        Args:
            function_type (string):
                The name for the type of function, this should match the
                filename that the class is stored in.

        Other KeyWord Args:
            All properties to be set on the function before building.
            Please see individual FunctionBuilders for more information.

        Returns:
            Function: Initialised function for use with firedrake.
        """
        func_builder = self.create_function_builder(function_type)

        try:
            for k, v in properties.items():
                func_builder.assign(k, v)
        except KeyError:
            raise ValueError('Could not create {} function with properties: {}'
                             ''.format(function_type, properties))

        return func_builder.build()

    def create_function_dict(self, conf):
        """
        Create a dictionary of all functions from a dictionary
        (or configparser).

        Args:
            conf (dict):
                The configuration to parse into a list of functions.
                e.g. {'f1.type': 'constant', 'f1.mean': '2e-5', 'f1.sd': ...,
                      'f2.type': ..., ...}

        Returns:
            dict: A dictionary with key as the names from files and val as a
                complete function.
        """
        all_funcs = {}
        for k, v in conf.items():
            name, prop = k.lower().split('.')
            if name not in all_funcs:
                all_funcs[name] = {}

            all_funcs[name][prop] = process_arg(v)

        funcs_dict = {}
        for name, f_dict in all_funcs.items():
            f_type = f_dict.pop('type')
            funcs_dict[name.lower()] = self.create_function(f_type, **f_dict)

        return funcs_dict
