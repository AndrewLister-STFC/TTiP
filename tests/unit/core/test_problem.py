"""
Test the problem.py file.

No tests for init, _A, _f as these just declare something.
"""
import unittest

from firedrake import Function, FunctionSpace, UnitCubeMesh, dx
from TTiP.core import problem


# pylint: disable=protected-access
class TestUpdateFunc(unittest.TestCase):
    """
    Test that _update_func substitues correctly.
    """

    def setUp(self):
        """
        Create a blank problem.
        """
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)

        self.prob = problem.Problem(mesh=self.mesh, V=self.V)

    def test_update_single_attr(self):
        """
        Test updating works for a single attribute.
        """
        attrs = vars(self.prob).copy()
        old_J = Function(self.V)
        new_J = Function(self.V)
        self.prob.J = old_J

        self.prob._update_func('J', new_J)

        # No change to existing vars
        for a, v in attrs.items():
            self.assertEqual(v, getattr(self.prob, a))

        # Change J
        self.assertEqual(self.prob.J, new_J)
        self.assertNotEqual(self.prob.J, old_J)

    def test_update_multiple_attr(self):
        """
        Test that updates propagate as expected.
        """
        attrs = vars(self.prob).copy()
        old_J = Function(self.V)
        new_J = Function(self.V)

        old_P = old_J**2*dx
        new_P = new_J**2*dx

        self.prob.J = old_J
        self.prob.P = old_P

        self.prob._update_func('J', new_J)

        # No change to existing vars
        for a, v in attrs.items():
            self.assertEqual(v, getattr(self.prob, a))

        # Change J
        self.assertNotEqual(self.prob.J, old_J, 'New J is equal to old J')
        self.assertEqual(self.prob.J, new_J, 'J is not correct')
        # Change P
        self.assertNotEqual(self.prob.P, old_P, 'New P is equal to old P')
        self.assertEqual(self.prob.P, new_P, 'P is not correct')


# pylint: disable=no-self-use
class TestSteadyStateProblem(unittest.TestCase):
    """
    Simple tests for the SteadyStateProblem class.
    """

    def test_can_initialise(self):
        """
        Test that the SteadyStateProblems can be instantiated.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        _ = problem.SteadyStateProblem(m, V)


class TestTimeDependantProblem(unittest.TestCase):
    """
    Simple tests for the TimeDependantProblem class.
    """

    def test_can_initialise(self):
        """
        Test that the TimeDependantProblem can be instantiated.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        _ = problem.TimeDependantProblem(m, V)
