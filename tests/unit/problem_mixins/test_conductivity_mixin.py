"""
Tests for the conductivity_mixin.py file.

Note: All of these funcs are either pass throughs or declarations.
As such, any tests would either repeat unit tests on the pass through,
or repeat the definition of the declaration.
Here we only test that it can be initialised.
"""
from unittest import TestCase

from firedrake import FunctionSpace, UnitCubeMesh

from TTiP.core.problem import Problem
from TTiP.problem_mixins.conductivity_mixin import (ConductivityLimiterMixin,
                                                    SpitzerHarmMixin)


# =============================================================================
# ========== SpitzerHarmMixin =================================================
# =============================================================================

class TestSHInit(TestCase):
    """
    Test initialsing with this mixin.
    """

    def setUp(self):
        """
        Create mesh and fnction space.
        """

        class MockProblem(SpitzerHarmMixin, Problem):
            """
            Fake problem to test the spitzer harm mixin.
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
        self.assertTrue(hasattr(prob, 'coulomb_ln'))
        self.assertTrue(hasattr(prob, 'ionisation'))


# =============================================================================
# ========== ConductivityLimiterMixin =========================================
# =============================================================================

class TestCLInit(TestCase):
    """
    Test initialsing with this mixin.
    """

    def setUp(self):
        """
        Create mesh and fnction space.
        """

        class MockProblem(ConductivityLimiterMixin, Problem):
            """
            Fake problem to test the spitzer harm mixin.
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
        self.assertTrue(hasattr(prob, 'ion_density'))
        self.assertTrue(hasattr(prob, 'ionisation'))
