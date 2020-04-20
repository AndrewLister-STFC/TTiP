"""
Tests for the core/iteration_method.py file.
"""
import unittest

from firedrake import Function, FunctionSpace, UnitCubeMesh, dx
from TTiP.core import iteration_method


class MockProblem:
    """
    A mock problem to allow simpler declaration of IterationMethod instances.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        """
        Set up the required attributes for initialising an IterationMethod.
        """
        self.T = None
        self.T_ = None


class TestUpdate(unittest.TestCase):
    """
    Test the update method.
    """

    def setUp(self):
        """
        Set up a problem and IterationMethod as all tests need these.
        """
        self.problem = MockProblem()
        self.im = iteration_method.IterationMethod(self.problem)

    def test_hidden_method(self):
        """
        Test that access to hidden variables is not allowed.
        """
        # pylint: disable=protected-access
        self.im._FakeMethod = lambda x: 'Fail'
        with self.assertRaises(ValueError):
            self.im.update(None, method='_FakeMethod')

    def test_nonexistent_method(self):
        """
        Test the expected exception is raised for nonexistent methods.
        """
        with self.assertRaises(ValueError):
            self.im.update(None, method='FakeMethod')

    def test_correct_method(self):
        """
        Test the correct args are passed to methods that do exist.
        """
        F = 'test_string'
        method = 'FakeMethod'
        setattr(self.im, method, self.stash_args)
        self.im.update(F=F, method=method, key_arg1='this', foo='bar')
        args, kwargs = self.stashed_args

        self.assertEqual(len(args), 1)
        self.assertEqual(F, args[0])

        self.assertIn('key_arg1', kwargs)
        self.assertEqual(kwargs['key_arg1'], 'this')

        self.assertIn('foo', kwargs)
        self.assertEqual(kwargs['foo'], 'bar')

    def stash_args(self, *args, **kwargs):
        """
        Utility function to store args in self.
        Used to replace a function in the above test.
        """
        #pylint: disable=attribute-defined-outside-init
        self.stashed_args = (args, kwargs)


class TestBackwardEuler(unittest.TestCase):
    """
    Test the BackwardEuler method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)
        self.T = Function(V)
        self.T_ = Function(V)

        p = MockProblem()
        p.T = self.T
        p.T_ = self.T_
        self.problem = p
        self.im = iteration_method.IterationMethod(self.problem)

    def test_correct_substitution(self):
        """
        Test the substitution is correct.
        """
        F_in = self.T*dx
        F = self.im.BackwardEuler(F_in)
        self.assertEqual(F, self.T*dx)


class TestForwardEuler(unittest.TestCase):
    """
    Test the ForwardEuler method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)
        self.T = Function(V)
        self.T_ = Function(V)

        p = MockProblem()
        p.T = self.T
        p.T_ = self.T_
        self.problem = p
        self.im = iteration_method.IterationMethod(self.problem)

    def test_correct_substitution(self):
        """
        Test the substitution is correct.
        """
        F_in = self.T*dx
        F = self.im.ForwardEuler(F_in)
        self.assertEqual(F, self.T_*dx)


class TestCrankNicolson(unittest.TestCase):
    """
    Test the CrankNicolson method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)
        self.T = Function(V)
        self.T_ = Function(V)

        p = MockProblem()
        p.T = self.T
        p.T_ = self.T_
        self.problem = p
        self.im = iteration_method.IterationMethod(self.problem)

    def test_correct_substitution(self):
        """
        Test the substitution is correct.
        """
        F_in = self.T*dx
        F = self.im.CrankNicolson(F_in)
        self.assertEqual(F, (0.5*(self.T+self.T_))*dx)


class TestTheta(unittest.TestCase):
    """
    Test the Theta method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)
        self.T = Function(V)
        self.T_ = Function(V)

        p = MockProblem()
        p.T = self.T
        p.T_ = self.T_
        self.problem = p
        self.im = iteration_method.IterationMethod(self.problem)

    def test_correct_substitution_0p2(self):
        """
        Test the substitution is correct for theta=0.2.
        """
        F_in = self.T*dx
        F = self.im.Theta(F_in, theta=0.2)
        self.assertEqual(F, (0.2*self.T + 0.8*self.T_)*dx)

    def test_correct_substitution_1p0(self):
        """
        Test the substitution is correct for theta=1.0.
        """
        F_in = self.T*dx
        F = self.im.Theta(F_in, theta=1.0)
        self.assertEqual(F, self.T*dx)

    def test_correct_substitution_0p5(self):
        """
        Test the substitution is correct for theta=0.5.
        """
        F_in = self.T*dx
        F = self.im.Theta(F_in, theta=0.5)
        self.assertEqual(F, (0.5*self.T + 0.5*self.T_)*dx)
