"""
Test for the parameters_parser.py file.
"""

import unittest

from firedrake import Constant, FunctionSpace, UnitCubeMesh
from TTiP.parsers.parameters_parser import ParametersParser


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
        self.parser = ParametersParser(mesh=mesh, V=V)

    def test_single_const(self):
        """
        Test that the density value is correctly returned for a single
        constant.
        """
        conf = {'electron_density.type': 'constant',
                'electron_density.value': '2.6'}

        self.parser.parse(conf)
        density = self.parser.parameters['electron_density']

        self.assertIsInstance(density, Constant)
        self.assertEqual(density([0.2, 1.0, 0.4]), 2.6)
