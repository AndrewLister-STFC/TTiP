"""
Tests for the function_builder.py file
"""
import unittest

from firedrake import FunctionSpace, UnitCubeMesh

from TTiP.function_builders.function_builder import FunctionBuilder


class DummyFunctionBuilder(FunctionBuilder):
    """
    A dummy function to allow creating an instance of the abstract base class.
    """
    properties = {'a': (int, float),
                  'b': (str)}

    def build(self):
        """
        Override abstract method.
        """


class TestAssign(unittest.TestCase):
    """
    Tests for the assign method.
    """

    def setUp(self):
        """
        Define the function builder.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)
        self.func_builder = DummyFunctionBuilder(m, V)

    def test_assign_valid_values(self):
        """
        Test that assign sets values correctly.
        """
        # pylint: disable=protected-access
        self.assertIs(self.func_builder._props['a'], None)
        self.assertIs(self.func_builder._props['b'], None)
        self.func_builder.assign('a', 10)
        self.func_builder.assign('b', 'ten')
        self.assertEqual(self.func_builder._props['a'], 10)
        self.assertEqual(self.func_builder._props['b'], 'ten')

    def test_assign_invalid_values(self):
        """
        Test that assign raises an error when the wrong type is given.
        """
        with self.assertRaises(TypeError):
            self.func_builder.assign('a', 'ten')

    def test_assign_invalid_name(self):
        """
        Test that assign raises an error when an unknown param is passed.
        """
        with self.assertRaises(KeyError):
            self.func_builder.assign('c', 10)
