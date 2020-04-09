"""
Test for the initial_vals_parser.py file.
"""

import unittest

from firedrake import Constant, FunctionSpace, UnitCubeMesh
from TTiP.parsers.initial_vals_parser import InitialValParser
from ufl.algebra import Sum


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
        self.parser = InitialValParser(mesh=mesh, V=V)

    def test_single_const(self):
        """
        Test that the initial value is correctly returned for a single
        constant.
        """
        conf = {'single.type': 'constant',
                'single.value': '2.6'}

        self.parser.parse(conf)
        iv = self.parser.initial_val

        self.assertIsInstance(iv, Constant)
        self.assertEqual(iv([0.2, 1.0, 0.4]), 2.6)

    def test_multiple_const(self):
        """
        Test that the initial value is correctly returned for multiple
        constants.
        """
        conf = {'single.type': 'constant',
                'single.value': '2.6',
                'next.type': 'Constant',
                'next.value': '-3'}

        self.parser.parse(conf)
        iv = self.parser.initial_val

        self.assertIsInstance(iv, Sum)
        self.assertEqual(iv([0.2, 1.0, 0.4]), 2.6-3)
