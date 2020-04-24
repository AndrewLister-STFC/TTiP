"""
Tests for the boundaries_mixin.py file.
"""

from unittest import TestCase

from firedrake import (DirichletBC, FacetNormal, Function, FunctionSpace,
                       UnitCubeMesh, dot, ds, dx, grad)
from mock import patch
from TTiP.core.problem import Problem
from TTiP.problem_mixins.boundaries_mixin import BoundaryMixin


# pylint: disable=protected-access
class MockProblem(BoundaryMixin, Problem):
    """
    Fake problem for testing the boundary mixin.
    """


class TestAddBoundry(TestCase):
    """
    Tests for the add_boundary method.
    """

    def setUp(self):
        """
        Prepare for tests.
        """
        self.args = []
        self.kwargs = {}
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)
        self.problem = MockProblem(mesh, V)

    def add_fake(self, *args, **kwargs):
        """
        Saves the args to self.args, and kwargs to self.kwargs.
        Used to mock add_<boundary_type> methods.
        """
        self.args = args
        self.kwargs = kwargs

    def test_robin(self):
        """
        Test with the robin boundary type.
        """
        with patch.object(self.problem, 'add_robin', self.add_fake):
            self.problem.add_boundary('robin', alpha=12.0, g='foo')

        self.assertTupleEqual(self.args, ())
        self.assertDictEqual({'alpha': 12.0, 'g': 'foo'}, self.kwargs)

    def test_dirichlet(self):
        """
        Test with the dirichlet boundary type.
        """
        with patch.object(self.problem, 'add_dirichlet', self.add_fake):
            self.problem.add_boundary('dirichlet', g=18.1)

        self.assertTupleEqual(self.args, ())
        self.assertDictEqual({'g': 18.1}, self.kwargs)

    def test_unknown(self):
        """
        Test with an unknown boundary type.
        """
        with self.assertRaises(ValueError):
            self.problem.add_boundary('fake_type', k=1, j='baz')


class TestAddDirichlet(TestCase):
    """
    Tests for he add_dirichlet method.
    """

    def setUp(self):
        """
        Prepare for tests.
        """
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)
        self.problem = MockProblem(self.mesh, self.V)
        self.norm = FacetNormal(self.mesh)

    def test_creates_boundary_cond_all(self):
        """
        Test that a boundary condition is added to the bcs attribte.
        """
        self.problem.add_dirichlet(10, 'all')
        self.assertEqual(len(self.problem.bcs), 1)
        self.assertIsInstance(self.problem.bcs[0], DirichletBC)

    def test_update_a_all_surface(self):
        """
        Test a is updated correctly for a with 'all' surface.
        """
        T = self.problem.T
        v = self.problem.v
        K = self.problem.K
        self.problem.a = T * dx

        g = Function(self.V)
        expected_a = T * dx + -1 * K * v * dot(grad(T), self.norm) * ds

        self.problem.add_dirichlet(g, 'all')

        self.assertEqual(expected_a, self.problem.a)

    def test_creates_boundary_cond_single_surface(self):
        """
        Test that a boundary condition is added to the bcs attribte.
        """
        self.problem.add_dirichlet(10, 1)
        self.assertEqual(len(self.problem.bcs), 1)
        self.assertIsInstance(self.problem.bcs[0], DirichletBC)

    def test_update_a_single_surface(self):
        """
        Test a is updated correctly for a with a single surface.
        """
        T = self.problem.T
        v = self.problem.v
        K = self.problem.K
        self.problem.a = T * dx

        g = Function(self.V)
        expected_a = T * dx + -1 * K * v * dot(grad(T), self.norm) * ds(0)

        self.problem.add_dirichlet(g, 0)

        self.assertEqual(expected_a, self.problem.a)

    def test_creates_boundary_cond_multiple_surfaces(self):
        """
        Test that a boundary condition is added to the bcs attribte.
        """
        self.problem.add_dirichlet(10, [0, 1, 2])
        self.assertEqual(len(self.problem.bcs), 1)
        self.assertIsInstance(self.problem.bcs[0], DirichletBC)

    def test_update_a_multiple_surfaces(self):
        """
        Test a is updated correctly for a with a multiple surfaces.
        """
        T = self.problem.T
        v = self.problem.v
        K = self.problem.K
        self.problem.a = T * dx

        g = Function(self.V)
        expected_a = T * dx + -1 * K * v * dot(grad(T), self.norm) * ds(0)
        expected_a += -1 * K * v * dot(grad(T), self.norm) * ds(1)

        self.problem.add_dirichlet(g, [0, 1])

        self.assertEqual(expected_a, self.problem.a)

    def test_sets_has_boundary(self):
        """
        Test that adding a boundary sets _has_boundary.
        """
        self.problem.add_dirichlet(10, [0, 1, 2])
        self.assertTrue(self.problem._has_boundary)

    def test_fails_has_value_false(self):
        """
        Test that exception raised if already set no boundaries explicitly.
        """
        self.problem._has_boundary = False
        with self.assertRaises(AttributeError):
            self.problem.add_dirichlet(10, 'all')


class TestAddRobin(TestCase):
    """
    Test for the add_robin method.
    """

    def setUp(self):
        """
        Prepare for tests.
        """
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)
        self.problem = MockProblem(self.mesh, self.V)

    def test_sets_has_boundary(self):
        """
        Test that adding a boundary sets _has_boundary
        """
        self.problem.add_robin(10, 10, [0, 1, 2])
        self.assertTrue(self.problem._has_boundary)

    def test_fails_has_boundary_false(self):
        """
        Test that exception raised if already set no boundaries explicitly.
        """
        self.problem._has_boundary = False
        with self.assertRaises(AttributeError):
            self.problem.add_robin(10, 10, 'all')

    def test_updates_single_surface(self):
        """
        Test that a and L are set correctly for a single surface.
        """
        T = self.problem.T
        v = self.problem.v
        self.problem.a = T * dx
        self.problem.L = T * dx

        alpha = Function(self.V)
        g = Function(self.V)
        expected_a = T * dx + alpha * v * T * ds(0)
        expected_L = T * dx + v * g * ds(0)

        self.problem.add_robin(alpha, g, 0)

        self.assertEqual(expected_a, self.problem.a)
        self.assertEqual(expected_L, self.problem.L)

    def test_updates_all_surfaces(self):
        """
        Test that a and L are set correctly for 'all' surface.
        """
        T = self.problem.T
        v = self.problem.v
        self.problem.a = T * dx
        self.problem.L = T * dx

        alpha = Function(self.V)
        g = Function(self.V)
        expected_a = T * dx + alpha * v * T * ds
        expected_L = T * dx + v * g * ds

        self.problem.add_robin(alpha, g, 'all')

        self.assertEqual(expected_a, self.problem.a)
        self.assertEqual(expected_L, self.problem.L)

    def test_updates_multiple_surfaces(self):
        """
        Test that a and L are set correctly for two surfaces.
        """
        T = self.problem.T
        v = self.problem.v
        self.problem.a = T * dx
        self.problem.L = T * dx

        alpha = Function(self.V)
        g = Function(self.V)
        expected_a = T * dx + alpha * v * T * ds(0) + alpha * v * T * ds(1)
        expected_L = T * dx + v * g * ds(0) + v * g * ds(1)

        self.problem.add_robin(alpha, g, [0, 1])

        self.assertEqual(expected_a, self.problem.a)
        self.assertEqual(expected_L, self.problem.L)


class TestSetNoBoundry(TestCase):
    """
    Tests for the set_no_boundary method.
    """

    def setUp(self):
        """
        Prepare for tests.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)
        self.problem = MockProblem(mesh, V)

    def test_sets_has_boundary(self):
        """
        Test that the function sets _has_boundary.
        """
        self.problem.set_no_boundary()
        self.assertFalse(self.problem._has_boundary)

    def test_fails_has_boundary_true(self):
        """
        Test that set_no_boundary raises error if already has boundary.
        """
        self.problem._has_boundary = True
        with self.assertRaises(AttributeError):
            self.problem.set_no_boundary()
