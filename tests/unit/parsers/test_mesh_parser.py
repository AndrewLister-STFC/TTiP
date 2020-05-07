"""
Tests for the mesh_parser.py file.
"""
import unittest
from unittest.mock import patch

from TTiP.parsers import mesh_parser


class TestParse(unittest.TestCase):
    """
    Tests for the parse method.
    """

    def setUp(self):
        """
        Create the parser.
        """
        self.parser = mesh_parser.MeshParser()
        self.args = ()
        self.kwargs = {}

    def test_cube_mesh_params_list(self):
        """
        Test that creating a unit cube works as expected, with 3 params.
        """
        expected = (10, 10, 10)
        conf = {'type': 'UnitCube',
                'params': '10, 10, 10',
                'element': 'CG',
                'order': 1}

        def fake_mesh_maker(*args, **kwargs):
            self.args = args

        def fake_function_space(*args, **kwargs):
            pass

        with patch.object(mesh_parser.firedrake,
                          'UnitCubeMesh',
                          fake_mesh_maker):
            with patch.object(mesh_parser.firedrake,
                              'FunctionSpace',
                              fake_function_space):
                self.parser.parse(conf)

        self.assertTupleEqual(self.args, expected)

    def test_cube_mesh_named_params(self):
        """
        Test that creating a unit cube works as expected, with 3 named params.
        """
        expected = {'nx': 10,
                    'ny': 10,
                    'nz': 10}

        conf = {'type': 'UnitCube',
                'nx': '10',
                'ny': '10',
                'nz': '10',
                'element': 'foo',
                'order': 6}

        def fake_mesh_maker(*args, **kwargs):
            self.kwargs = kwargs

        def fake_function_space(*args, **kwargs):
            pass

        with patch.object(mesh_parser.firedrake,
                          'UnitCubeMesh',
                          fake_mesh_maker):
            with patch.object(mesh_parser.firedrake,
                              'FunctionSpace',
                              fake_function_space):
                self.parser.parse(conf)

        self.assertTupleEqual(self.args, ())
        self.assertDictEqual(self.kwargs, expected)
