"""
Tests for the specific_heat_capacity_mixin.py file.

Note: All of the funcs in this file are either pass throughs or declarations.
As such, any tests would either repeat unit tests on the pass through,
or repeat the definition of the declaration.
Here we only test that it can be initialised.
"""
from unittest import TestCase

from firedrake import FunctionSpace, UnitCubeMesh

from TTiP.core.problem import Problem
from TTiP.problem_mixins.specific_heat_capacity_mixin import (
    ConstantIonisationSHCMixin, NonConstantIonisationSHCMixin)


class TestConstantIonisationSHCMixinInit(TestCase):
    """
    Test initialising with this mixin.
    """

    def setUp(self):
        """
        Create mesh and function space.
        """

        class MockProblem(ConstantIonisationSHCMixin, Problem):
            """
            Fake problem to test the constant ionisation specific heat capacity
            mixin.
            """

        self.cls = MockProblem

        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)

    def test_can_create(self):
        """
        Test that the problem can be initialised.
        """
        self.cls(mesh=self.mesh, V=self.V)

    def test_has_attributes(self):
        """
        Test that the initialised problem has the required attributes.
        """
        prob = self.cls(mesh=self.mesh, V=self.V)
        self.assertTrue(hasattr(prob, 'electron_density'))
        self.assertTrue(hasattr(prob, 'C'))


class TestNonConstantIonisationSHCMixinInit(TestCase):
    """
    Test initialising with this mixin.
    """

    def setUp(self):
        """
        Create mesh and function space.
        """

        class MockProblem(NonConstantIonisationSHCMixin, Problem):
            """
            Fake problem to test the non-constant ionisation specific heat
            capacity mixin.
            """

        self.cls = MockProblem

        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)

    def test_can_create(self):
        """
        Test that the problem can be initialised.
        """
        self.cls(mesh=self.mesh, V=self.V)

    def test_has_attributes(self):
        """
        Test that the initialised problem has the required attributes.
        """
        prob = self.cls(mesh=self.mesh, V=self.V)
        self.assertTrue(hasattr(prob, 'ionisation'))
        self.assertTrue(hasattr(prob, 'ion_density'))
        self.assertTrue(hasattr(prob, 'C'))
