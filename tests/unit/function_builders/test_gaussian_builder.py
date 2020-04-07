import unittest

import numpy as np

from firedrake import FunctionSpace, UnitIntervalMesh
from TTiP.function_builders.gaussian_builder import GaussianBuilder


class TestBuild(unittest.TestCase):
    def setUp(self):
        m = UnitIntervalMesh(100)
        V = FunctionSpace(m, 'CG', 1)
        self.builder = GaussianBuilder(m, V)

    def test_value(self):

        self.builder.assign('mean', 0)
        self.builder.assign('sd', 1)
        self.builder.assign('scale', 1)
        actual = self.builder.build()
        expected = self.gaussian(0, 1, 1)

        points = [i/10 for i in range(11)]
        for p in points:
            self.assertAlmostEqual(actual(p), expected(p))

    def test_value_2(self):

        self.builder.assign('mean', 0.5)
        self.builder.assign('sd', 0.1)
        self.builder.assign('scale', 10)
        actual = self.builder.build()
        expected = self.gaussian(mean=0.5, sd=0.1, scale=10)

        points = [i/10 for i in range(11)]
        for p in points:
            self.assertAlmostEqual(actual(p), expected(p))

    def gaussian(self, mean, scale, sd):
        return lambda x: scale*np.exp(-0.5*np.dot((x-mean)/sd, (x-mean)/sd))
