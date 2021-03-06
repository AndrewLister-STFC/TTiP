"""
Tests for the time_mixin.py file.
"""
from unittest import TestCase

from firedrake import FunctionSpace, UnitCubeMesh
from mock import patch

from TTiP.core.problem import Problem
from TTiP.problem_mixins.time_mixin import IterationMethod, TimeMixin


# pylint: disable=attribute-defined-outside-init, protected-access, no-member
class MockProblem(TimeMixin, Problem):
    """
    A dummy class to allow instantiating the mixin.
    """


# =============================================================================
# ========== TIME MIXIN CLASS TESTS ===========================================
# =============================================================================

class TestSetMethod(TestCase):
    """
    Test for the set_method method.
    """

    def setUp(self):
        """
        Create the problem.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)
        self.stashed_args = ([], {})

    def stash_args(self, *args, **kwargs):
        """
        Utility function to take a copy of the args.
        Used to mock functions.
        """
        self.stashed_args = (args, kwargs)
        return self.problem.T_

    def test_get_correct_substitution(self):
        """
        Test that the method is passed to IterationMethod correctly.
        """
        with patch.object(IterationMethod,
                          'get_substitution',
                          self.stash_args):
            self.problem.set_method('fake', foo='bar', baz=2)

        args, kwargs = self.stashed_args
        self.assertTupleEqual(args, ('fake',))
        self.assertDictEqual(kwargs, {'foo': 'bar', 'baz': 2})

    def test_does_correct_substitution_T(self):
        """
        Test that functions on the problem are updated as expected
        (for the given method) with respect to T.
        """
        self.problem.Q = self.problem.T * self.problem.T

        with patch.object(IterationMethod,
                          'get_substitution',
                          self.stash_args):
            self.problem.set_method('fake')

        self.assertEqual(self.problem.Q, self.problem.T_ * self.problem.T_)

    def test_substitutes_delT(self):
        """
        Test that the functions on the problem are updated to remove delT as
        expected.
        """
        self.problem.Q = self.problem._delT * self.problem._delT
        T = self.problem.T
        T_ = self.problem.T_
        dt_inv = self.problem._dt_invc
        expected = ((T - T_) * dt_inv) * ((T - T_) * dt_inv)

        with patch.object(IterationMethod,
                          'get_substitution',
                          self.stash_args):
            self.problem.set_method('fake')

        self.assertEqual(self.problem.Q, expected)


class TestRemoveTimescale(TestCase):
    """
    Tests for the remove_timescale method.
    """

    def setUp(self):
        """
        Create a problem.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)

    def test_sets_steady_state(self):
        """
        Test that the bool is flipped to true.
        """
        self.problem.steady_state = False
        self.problem.remove_timescale()
        self.assertTrue(self.problem.steady_state)


class TestSetTimescale(TestCase):
    """
    Tests for the set_timescale method.
    """

    def setUp(self):
        """
        Create a problem.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)

    def test_sets_steady_state(self):
        """
        Test that steady_state is set to false.
        """
        self.problem.steady_state = True
        self.problem.set_timescale(dt=1, steps=1)
        self.assertFalse(self.problem.steady_state)

    def test_no_args(self):
        """
        Test that a ValueError is raised when no args are passed.
        """
        with self.assertRaises(ValueError):
            self.problem.set_timescale()

    def test_one_arg(self):
        """
        Test that a ValueError is raised when only one arg is passed.
        """
        with self.assertRaises(ValueError):
            self.problem.set_timescale(dt=1)

    def test_max_t_and_dt(self):
        """
        Test that steps is correctly calculated and values are stored correctly
        for given max_t and dt.
        """
        self.problem.set_timescale(max_t=5.3, dt=0.1)
        self.assertAlmostEqual(self.problem.max_t, 5.3)
        self.assertAlmostEqual(self.problem.dt, 0.1)
        self.assertEqual(self.problem.steps, 53)

    def test_max_t_and_steps(self):
        """
        Test that dt is correctly calculated and values are stored correctly
        for given max_t and steps.
        """
        self.problem.set_timescale(max_t=5.3, steps=53)
        self.assertAlmostEqual(self.problem.max_t, 5.3)
        self.assertAlmostEqual(self.problem.dt, 0.1)
        self.assertEqual(self.problem.steps, 53)

    def test_dt_and_steps(self):
        """
        Test that max_t is correctly calculated and values are stored correctly
        for given dt and steps.
        """
        self.problem.set_timescale(dt=0.1, steps=53)
        self.assertAlmostEqual(self.problem.max_t, 5.3)
        self.assertAlmostEqual(self.problem.dt, 0.1)
        self.assertEqual(self.problem.steps, 53)

    def test_all_args_consistent(self):
        """
        Test that values are set correctly when given all 3 args if they are
        consistent. (steps <= max_t/dt < steps + 1)
        """
        self.problem.set_timescale(max_t=5.3, dt=0.1, steps=53)
        self.assertAlmostEqual(self.problem.max_t, 5.3)
        self.assertAlmostEqual(self.problem.dt, 0.1)
        self.assertEqual(self.problem.steps, 53)

    def test_all_args_conflicting(self):
        """
        Test that ValueError is raised if args are inconsistent.
        (max_t/dt - 1  >= steps, or steps > max_t/dt)
        """
        with self.assertRaises(ValueError):
            self.problem.set_timescale(max_t=4.0, dt=0.1, steps=53)


# =============================================================================
# ========== ITERATION METHOD CLASS TESTS =====================================
# =============================================================================


class TestGetSubstitution(TestCase):
    """
    Test the get_substitution method.
    """

    def setUp(self):
        """
        Set up a problem and IterationMethod as all tests need these.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)
        self.im = IterationMethod(self.problem)

    def test_hidden_method(self):
        """
        Test that access to hidden variables is not allowed.
        """
        # pylint: disable=protected-access
        self.im._FakeMethod = lambda x: 'Fail'
        with self.assertRaises(ValueError):
            self.im.get_substitution(method='_FakeMethod')

    def test_nonexistent_method(self):
        """
        Test the expected exception is raised for nonexistent methods.
        """
        with self.assertRaises(ValueError):
            self.im.get_substitution(method='FakeMethod')

    def test_correct_method(self):
        """
        Test the correct args are passed to methods that do exist.
        """
        method = 'FakeMethod'
        setattr(self.im, method, self.stash_args)
        self.im.get_substitution(method=method, key_arg1='this', foo='bar')
        args, kwargs = self.stashed_args

        self.assertEqual(len(args), 0)

        self.assertIn('key_arg1', kwargs)
        self.assertEqual(kwargs['key_arg1'], 'this')

        self.assertIn('foo', kwargs)
        self.assertEqual(kwargs['foo'], 'bar')

    def stash_args(self, *args, **kwargs):
        """
        Utility function to store args in self.
        Used to replace a function in the above test.
        """
        # pylint: disable=attribute-defined-outside-init
        self.stashed_args = (args, kwargs)


class TestBackwardEuler(TestCase):
    """
    Test the BackwardEuler method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)
        self.im = IterationMethod(self.problem)

    def test_correct_substitution(self):
        """
        Test the substitution is correct.
        """
        actual = self.im.BackwardEuler()
        expected = self.problem.T
        self.assertEqual(actual, expected)


class TestForwardEuler(TestCase):
    """
    Test the ForwardEuler method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)
        self.im = IterationMethod(self.problem)

    def test_correct_substitution(self):
        """
        Test the substitution is correct.
        """
        actual = self.im.ForwardEuler()
        expected = self.problem.T_
        self.assertEqual(actual, expected)


class TestCrankNicolson(TestCase):
    """
    Test the CrankNicolson method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)
        self.im = IterationMethod(self.problem)

    def test_correct_substitution(self):
        """
        Test the substitution is correct.
        """
        actual = self.im.CrankNicolson()
        expected = 0.5 * (self.problem.T + self.problem.T_)
        self.assertEqual(actual, expected)


class TestTheta(TestCase):
    """
    Test the Theta method.
    """

    def setUp(self):
        """
        Define 2 functions and create an IterationMethod.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = MockProblem(m, V)
        self.im = IterationMethod(self.problem)

    def test_correct_substitution_0p2(self):
        """
        Test the substitution is correct for theta=0.2.
        """
        actual = self.im.Theta(theta=0.2)
        expected = 0.2*self.problem.T + 0.8*self.problem.T_
        self.assertEqual(actual, expected)

    def test_correct_substitution_1p0(self):
        """
        Test the substitution is correct for theta=1.0.
        """
        actual = self.im.Theta(theta=1.0)
        expected = self.problem.T
        self.assertEqual(actual, expected)

    def test_correct_substitution_0p5(self):
        """
        Test the substitution is correct for theta=0.5.
        """
        actual = self.im.Theta(theta=0.5)
        expected = 0.5*self.problem.T + 0.5*self.problem.T_
        self.assertEqual(actual, expected)
