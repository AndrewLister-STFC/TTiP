"""
Tests for the function_builder_factory.py file.
"""
import unittest

import numpy as np

from firedrake import Constant, Function, FunctionSpace, UnitCubeMesh, UnitSquareMesh
from TTiP.function_builders.constant_builder import ConstantBuilder
from TTiP.function_builders.function_builder_factory import \
    FunctionBuilderFactory
from TTiP.function_builders.gaussian_builder import GaussianBuilder
from ufl.algebra import Sum


class TestCreateFunctionBuilder(unittest.TestCase):
    """
    Test the create_function_builder method.
    """

    def setUp(self):
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)
        self.factory = FunctionBuilderFactory(mesh=mesh, V=V)

    def test_create_constant_builder(self):
        """
        Test that passing constant returns a constant builder.
        """
        func = self.factory.create_function_builder('constant')
        self.assertIsInstance(func, ConstantBuilder)

    def test_nonexistant_function_type(self):
        """
        Test the expected behaiour for non existant functions.
        """
        with self.assertRaises(ImportError):
            self.factory.create_function_builder('NotAFunction')


class TestCreateFunction(unittest.TestCase):
    """
    Tests for the create_function method.
    """

    def setUp(self):
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)
        self.factory = FunctionBuilderFactory(mesh=mesh, V=V)

    def test_create_constant_function(self):
        """
        Test that a constant function can be created.
        """
        val = 1.2
        func = self.factory.create_function('constant', value=val)
        points = [i/10 for i in range(11)]

        for p in points:
            self.assertAlmostEqual(func(p), val)

    def test_wrong_property_name(self):
        """
        Test that an error is raised for a function generated with a wrong
        property.
        """
        with self.assertRaises(ValueError):
            self.factory.create_function('constant', not_valid=1.0)

    def test_wrong_property_type(self):
        """
        Test that an error is raised for a function generated with a correct
        property but of the wrong type.
        """
        with self.assertRaises(TypeError):
            self.factory.create_function('constant', value='a string')

    def test_missing_properties(self):
        """
        Test that an appropriate error is raised when a property is not
        defined.
        """
        with self.assertRaises(AttributeError):
            self.factory.create_function('constant')


class TestCreateFunctionDict(unittest.TestCase):
    """
    Test the create_function_dict method.
    """

    def setUp(self):
        mesh = UnitSquareMesh(100, 100)
        V = FunctionSpace(mesh, 'CG', 1)
        self.factory = FunctionBuilderFactory(mesh=mesh, V=V)

    def test_correct_func_types(self):
        """
        Test that the functions in the dictionary are valid Functions.
        """
        conf = {
            'func1.type': 'constant',
            'func1.value': '1.9',
            'another_one.type': 'gaussian',
            'another_one.mean': '0.1, 2.0',
            'another_one.sd': '0.1',
            'another_one.scale': '10'}

        fdict = self.factory.create_function_dict(conf)
        for v in fdict.values():
            self.assertIsInstance(v, (Function, Constant, Sum))

    def test_correct_func_values(self):
        """
        Test that the functions in the dictionary return the expected values.
        """
        const_val = 1.9
        gaus_mean = 0.5
        gaus_sd = 0.5
        gaus_scale = 10.0

        def const_analytical(x): return const_val

        def gaus_analytical(x):
            return gaus_scale*np.exp(-0.5*(np.dot((x-gaus_mean)/gaus_sd,
                                                  (x-gaus_mean)/gaus_sd)))

        points = [np.array([i/11, j/11])
                  for i in range(11)
                  for j in range(11)]

        conf = {
            'func1.type': 'constant',
            'func1.value': str(const_val),
            'another_one.type': 'gaussian',
            'another_one.mean': str(gaus_mean),
            'another_one.sd': str(gaus_sd),
            'another_one.scale': str(gaus_scale)}

        fdict = self.factory.create_function_dict(conf)

        for p in points:
            self.assertAlmostEqual(fdict['func1'](p),
                                   const_analytical(p))
            self.assertAlmostEqual(fdict['another_one'](p),
                                   gaus_analytical(p), places=2)
