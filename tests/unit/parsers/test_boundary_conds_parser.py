"""
Test for the boundary_conds_parser.py file.
"""

import unittest

from firedrake import Constant, FunctionSpace, UnitCubeMesh
from TTiP.parsers.boundary_conds_parser import BoundaryCondsParser


class TestParse(unittest.TestCase):
    """
    Tests for the parse method.
    """

    def setUp(self):
        """
        Create the parser.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)
        self.parser = BoundaryCondsParser(mesh=mesh, V=V)

    def test_single_const_dirichlet(self):
        """
        Test the parser with a single, simple boundary condition.
        """
        conf = {'single.boundary_type': 'dirichlet',
                'single.g': '3',
                'single.surface': 'all'}

        expected = {'boundary_type': 'dirichlet',
                    'g': 3,
                    'surface': 'all'}

        self.parser.parse(conf)
        bcs = self.parser.bcs

        self.assertEqual(len(bcs), 1)
        self.assertDictEqual(bcs[0], expected)

    def test_mulitple_const(self):
        """
        Test the parser with 3, simple boundary conditions.
        """
        conf = {'foo.boundary_type': 'dirichlet',
                'foo.g': '3',
                'foo.surface': '5, 6',
                'bar.boundary_type': 'robin',
                'bar.alpha': '1.2',
                'bar.g': '13',
                'bar.surface': '4',
                'baz.boundary_type': 'dirichlet',
                'baz.g': '0.1',
                'baz.surface': '1, 2, 3'}

        expected = [{'boundary_type': 'dirichlet',
                     'g': 3,
                     'surface': [5, 6]},
                    {'boundary_type': 'robin',
                     'alpha': 1.2,
                     'g': 13,
                     'surface': 4},
                    {'boundary_type': 'dirichlet',
                     'g': 0.1,
                     'surface': [1, 2, 3]}]

        self.parser.parse(conf)
        bcs = self.parser.bcs

        self.assertEqual(len(bcs), 3)

        for bc in bcs:
            for e in expected:
                if dict_equal(bc, e):
                    break
            else:
                self.fail('Unexpected boundary condition: {}'.format(bc))

    def test_single_function_dirichlet(self):
        """
        Test the parser with a single dirichlet condition where g is a
        Function.
        """
        conf = {'single.boundary_type': 'dirichlet',
                'single.g.type': 'constant',
                'single.g.value': '8',
                'single.surface': 'all'}

        expected = {'boundary_type': 'dirichlet',
                    'g': 8,
                    'surface': 'all'}

        self.parser.parse(conf)
        bcs = self.parser.bcs

        self.assertEqual(len(bcs), 1)

        actual_g = bcs[0].pop('g')
        expected_g = expected.pop('g')

        self.assertDictEqual(bcs[0], expected)
        self.assertIsInstance(actual_g, Constant)
        self.assertEqual(actual_g(0.5), expected_g)


def dict_equal(dict1, dict2):
    """
    Utility function to check if 2 dictionaries match.

    Args:
        dict1 (dict): The first dictionary.
        dict2 (dict): Thes second dictionary.
    """
    d1 = dict1.copy()
    d2 = dict2.copy()
    for k, v in d1.items():
        if k not in d2:
            return False

        if v != d2.pop(k):
            return False

    return d2 == {}
