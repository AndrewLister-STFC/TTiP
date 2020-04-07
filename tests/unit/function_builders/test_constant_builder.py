import unittest

from TTiP.function_builders.constant_builder import ConstantBuilder


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.builder = ConstantBuilder(None, None)

    def test_value(self):
        val = 3.0
        self.builder.assign('value', val)
        constant = self.builder.build()

        points = [i/10 for i in range(11)]
        for p in points:
            self.assertAlmostEqual(constant(p), val)

    def test_value_2(self):
        val = 18.6
        self.builder.assign('value', val)
        constant = self.builder.build()

        points = [i/10 for i in range(11)]
        for p in points:
            self.assertAlmostEqual(constant(p), val)
