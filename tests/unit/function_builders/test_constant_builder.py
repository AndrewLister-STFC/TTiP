"""
The tests for the constant_builder.py file.
"""
import unittest

from TTiP.function_builders.constant_builder import ConstantBuilder


class TestBuild(unittest.TestCase):
    """
    Test the build method.
    """
    def setUp(self):
        """
        Create a constant builder.
        """
        self.builder = ConstantBuilder(None, None)

    def test_value(self):
        """
        Test that the value is assigned correctly.
        """
        val = 3.0
        self.builder.assign('value', val)
        constant = self.builder.build()

        points = [i/10 for i in range(11)]
        for p in points:
            self.assertAlmostEqual(constant(p), val)

    def test_value_2(self):
        """
        Test another value.
        """
        val = 18.6
        self.builder.assign('value', val)
        constant = self.builder.build()

        points = [i/10 for i in range(11)]
        for p in points:
            self.assertAlmostEqual(constant(p), val)
