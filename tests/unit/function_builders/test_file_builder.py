"""
Contains tests for the file_bulder.py file.
"""

from tempfile import NamedTemporaryFile
from unittest import TestCase

import numpy as np
from firedrake import FunctionSpace, UnitCubeMesh, UnitSquareMesh

from TTiP.function_builders.file_builder import FileBuilder


class TestGeneralBuild(TestCase):
    """
    Tests for the build method in general.
    """

    def test_no_path(self):
        """
        Test error is raised if path is not set.
        """
        fb = FileBuilder(None, None)

        with self.assertRaises(AttributeError):
            fb.build()

    def test_non_existant_path(self):
        """
        Test error is raised when path does not exist.
        """
        fb = FileBuilder(None, None)
        fb.assign('path', './a_fake_file_1234.xyz')

        with self.assertRaises(ValueError):
            fb.build()


class Test2dBuild(TestCase):
    """
    Tests for the build method with a 2d mesh.
    """

    def setUp(self):
        """
        Create a function builder and input file.
        """
        self.mesh = UnitSquareMesh(10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)
        self.fb = FileBuilder(self.mesh, self.V)

        self.input = NamedTemporaryFile(mode='w+')
        self.fb.assign('path', self.input.name)

    def test_build_constant(self):
        """
        Test interpolation is correct for a 2d constant valued file.
        """
        lines = ['#   x,   y,    v\n']
        lines += [f'{x}, {y}, 10.0\n'
                  for x in np.linspace(0.0, 1.0, 11)
                  for y in np.linspace(0.0, 1.0, 11)]

        self.input.writelines(lines)
        self.input.flush()

        f = self.fb.build()

        self.assertAlmostEqual(f((0.0, 0.0)), 10.0)
        self.assertAlmostEqual(f((0.0, 0.15)), 10.0)
        self.assertAlmostEqual(f((0.38, 0.62)), 10.0)
        self.assertAlmostEqual(f((0.99, 0.99)), 10.0)

    def test_build_linear(self):
        """
        Test interpolarion is correct for a 2d linear valued the file.
        """
        lines = ['#   x,   y,   v\n']
        lines += [f'{x}, {y}, {10*(x+y)}\n'
                  for x in np.linspace(0.0, 1.0, 11)
                  for y in np.linspace(0.0, 1.0, 11)]

        self.input.writelines(lines)
        self.input.flush()

        f = self.fb.build()

        self.assertAlmostEqual(f((0.0, 0.0)), 0.0)
        self.assertAlmostEqual(f((0.0, 0.15)), 1.5)
        self.assertAlmostEqual(f((0.38, 0.62)), 10.0)
        self.assertAlmostEqual(f((0.99, 0.99)), 19.8)


class Test3dBuild(TestCase):
    """
    Tests for the build method with a 3d mesh.
    """

    def setUp(self):
        """
        Create a function builder and input file.
        """
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)
        self.fb = FileBuilder(self.mesh, self.V)

        self.input = NamedTemporaryFile(mode='w+')
        self.fb.assign('path', self.input.name)

    def test_3d_constant(self):
        """
        Test interpolation is correct for a 3d constant valued file.
        """
        lines = ['#   x,   y,   z,    v\n']
        lines += [f'{x}, {y}, {z}, 10.0\n'
                  for x in np.linspace(0.0, 1.0, 11)
                  for y in np.linspace(0.0, 1.0, 11)
                  for z in np.linspace(0.0, 1.0, 11)]

        self.input.writelines(lines)
        self.input.flush()

        f = self.fb.build()

        self.assertAlmostEqual(f((0.0, 0.0, 0.0)), 10.0)
        self.assertAlmostEqual(f((0.0, 0.15, 0.94)), 10.0)
        self.assertAlmostEqual(f((0.38, 0.62, 0.01)), 10.0)
        self.assertAlmostEqual(f((0.99, 0.99, 0.54)), 10.0)

    def test_3d_linear(self):
        """
        Test interpolation is correct for a 3d linear valued file.
        """
        lines = ['#   x,   y,   z,    v\n']
        lines += [f'{x}, {y}, {z}, {10*(x+y+z)}\n'
                  for x in np.linspace(0.0, 1.0, 11)
                  for y in np.linspace(0.0, 1.0, 11)
                  for z in np.linspace(0.0, 1.0, 11)]

        self.input.writelines(lines)
        self.input.flush()

        f = self.fb.build()

        self.assertAlmostEqual(f((0.0, 0.0, 0.0)), 0.0)
        self.assertAlmostEqual(f((0.0, 0.15, 0.94)), 10.9)
        self.assertAlmostEqual(f((0.38, 0.62, 0.01)), 10.1)
        self.assertAlmostEqual(f((0.99, 0.99, 0.54)), 25.2)
