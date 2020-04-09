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

    def test_cube_mesh_params_list(self):
        """
        Test that creating a unit cube works as expected, with 3 params.
        """
        expected = (10, 10, 10)
        conf = {'type': 'UnitCube',
                'params': '10, 10, 10'}

        def fake_mesh_maker(*args, **kwargs):
            self.assertTupleEqual(args, expected)
            self.assertDictEqual(kwargs, {})

        with patch.object(mesh_parser.firedrake,
                          'UnitCubeMesh',
                          fake_mesh_maker):
            self.parser.parse(conf)

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
                'nz': '10'}

        def fake_mesh_maker(*args, **kwargs):
            self.assertTupleEqual(args, ())
            self.assertDictEqual(kwargs, expected)

        with patch.object(mesh_parser.firedrake,
                          'UnitCubeMesh',
                          fake_mesh_maker):
            self.parser.parse(conf)
