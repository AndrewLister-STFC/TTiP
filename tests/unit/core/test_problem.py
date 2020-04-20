"""
Test the problem.py file.

No tests for init, _A, _f as these just declare something.
"""
import unittest

from firedrake import Function, FunctionSpace, UnitCubeMesh, dx
from TTiP.core import problem


class TestSetS(unittest.TestCase):
    """
    Test that set_S substitues S correctly.
    """

    def test_set_S_works(self):
        """
        Test S correctly substitutes S.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        prob = problem.Problem(mesh=m, V=V)

        prob.L = prob.S*dx
        new_S = Function(V)
        new_L = new_S*dx
        prob.set_S(new_S)
        self.assertEqual(prob.L, new_L)
        self.assertEqual(prob.S, new_S)


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
