"""
This file contains the abstract base classes for the parsers.
"""
from abc import ABC, abstractmethod

from TTiP.function_builders.function_builder_factory import \
    FunctionBuilderFactory


class SectionParser(ABC):
    """
    The base class, defines the structure of parsers.
    """

    @abstractmethod
    def parse(self, conf):
        """
        Parse the config section into attributes.

        Args:
            conf (configparser section):
                The config section to parse.
        """
        return NotImplementedError('This is an abstract method.')


class FunctionSectionParser(SectionParser):
    """
    A base class for parsing sections which contain functions.

    Attributes:
        factory (FunctionBuilderFactory):
            A factory for generating functions from the config values.
    """
    def __init__(self, mesh, V):
        """
        Initialiser for the FunctionSectionParser.

        Args:
            mesh (Mesh):
                The mesh that the functions should be interpolated over.
            V (FunctionSpace):
                The function space that the functions should belong to.
        """
        super().__init__()
        self.factory = FunctionBuilderFactory(mesh, V)
