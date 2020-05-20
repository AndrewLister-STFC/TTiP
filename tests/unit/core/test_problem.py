"""
Test the problem.py file.

No tests for init, _A, _f as these just declare something.
"""
from unittest import TestCase
from unittest.mock import patch

from firedrake import (Function, FunctionSpace, SpatialCoordinate,
                       UnitCubeMesh, as_tensor, dx)

from TTiP.core import problem
from TTiP.problem_mixins.boundaries_mixin import BoundaryMixin
from TTiP.problem_mixins.conductivity_mixin import (ConductivityLimiterMixin,
                                                    SpitzerHarmMixin)
from TTiP.problem_mixins.flux_limit_mixin import FluxLimiterMixin
from TTiP.problem_mixins.specific_heat_capacity_mixin import (
    ConstantIonisationSHCMixin, NonConstantIonisationSHCMixin)
from TTiP.problem_mixins.time_mixin import TimeMixin


# pylint: disable=protected-access
class TestUpdateFunc(TestCase):
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

    def test_update_non_existant_var(self):
        """
        Test that an error is raised for a non-existing variable.
        """
        with self.assertRaises(AttributeError):
            self.prob._update_func('fake_func', None)

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


class TestSetFunction(TestCase):
    """
    Tests for the set_function method.
    """
    def setUp(self):
        """
        Create a blank problem.
        """
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)

        self.prob = problem.Problem(mesh=self.mesh, V=self.V)

        self.args = ()
        self.kwargs = {}

    def test_unmanaged_function(self):
        """
        Test that the function raises an exception if the name is not in the
        function list.
        """
        self.prob._functions = []

        with self.assertRaises(AttributeError):
            self.prob.set_function('foo', 3)

    def test_correct_call(self):
        """
        Test that the correct values are passed to _update_func.
        """
        self.prob._functions = ['foo']

        with patch.object(self.prob, '_update_func', self.stash_args):
            self.prob.set_function('foo', 3)

        self.assertTupleEqual(self.args, ())
        self.assertDictEqual(self.kwargs, {'name': 'foo', 'val': 3})

    def stash_args(self, *args, **kwargs):
        """
        Utility function to capture arguments from mocked out functions.
        """
        self.args = args
        self.kwargs = kwargs


class TestAddFunction(TestCase):
    """
    Tests for the _add_function method.
    """

    def setUp(self):
        """
        Create a blank problem.
        """
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)

        self.prob = problem.Problem(mesh=self.mesh, V=self.V)

    def test_creates_attribute(self):
        """
        Test that the function creates an attribute if none exists.
        """
        self.assertFalse(hasattr(self.prob, 'foo'))
        self.prob._add_function('foo')
        self.assertTrue(hasattr(self.prob, 'foo'))

    def test_existing_attribute(self):
        """
        Test that it does not change an existing function if call is repeated.
        """
        self.prob._add_function('foo')
        foo = self.prob.foo
        self.prob._add_function('foo')
        self.assertIs(foo, self.prob.foo)

    def test_existing_non_function_attribute(self):
        """
        Test that an exception is raised if the name exists and is not a
        function.
        """
        self.prob.foo = 'bar'
        with self.assertRaises(AttributeError):
            self.prob._add_function('foo')


class TestBound(TestCase):
    """
    Tests for the bound method.
    """

    def setUp(self):
        """
        Create a problem and function to set bounds on.
        """
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)

        self.prob = problem.Problem(mesh=self.mesh, V=self.V)

        self.prob.to_bound = Function(self.V)
        self.prob.test_func = self.prob.to_bound + 1

    def test_non_existant_function(self):
        """
        Test that an exception is raised if the name does not exist.
        """
        self.assertFalse(hasattr(self.prob, 'baz'))
        
        with self.assertRaises(AttributeError):
            self.prob.bound('baz', 1, 2)

    def test_set_no_bound(self):
        """
        Test that passing no bounds results in no change
        """
        to_bound = self.prob.to_bound
        test_func = self.prob.test_func
        self.prob.bound('to_bound')
        self.assertIs(to_bound, self.prob.to_bound)
        self.assertIs(test_func, self.prob.test_func)

    def test_lower_bound_scalar(self):
        """
        Test that setting lower bounds work as expected for normal functions.
        """
        x = SpatialCoordinate(self.mesh)
        self.prob.to_bound.interpolate(x[0])

        self.assertAlmostEqual(self.prob.test_func([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func([0.6, 0.1, 0.1]), 1.6)
        self.prob.bound('to_bound', lower=0.2)
        self.assertAlmostEqual(self.prob.test_func([0.1, 0.1, 0.1]), 1.2)
        self.assertAlmostEqual(self.prob.test_func([0.6, 0.1, 0.1]), 1.6)

    def test_upper_bound_scalar(self):
        """
        Test that setting upper bounds work as expected for normal functions.
        """
        x = SpatialCoordinate(self.mesh)
        self.prob.to_bound.interpolate(x[0])

        self.assertAlmostEqual(self.prob.test_func([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func([0.6, 0.1, 0.1]), 1.6)
        self.prob.bound('to_bound', upper=0.2)
        self.assertAlmostEqual(self.prob.test_func([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func([0.6, 0.1, 0.1]), 1.2)

    def test_upper_and_lower_bound_scalar(self):
        """
        Test that setting lower and upper bounds work as expected for normal
        functions.
        """
        x = SpatialCoordinate(self.mesh)
        self.prob.to_bound.interpolate(x[0])

        self.assertAlmostEqual(self.prob.test_func([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func([0.6, 0.1, 0.1]), 1.6)
        self.prob.bound('to_bound', lower=0.2, upper=0.5)
        self.assertAlmostEqual(self.prob.test_func([0.1, 0.1, 0.1]), 1.2)
        self.assertAlmostEqual(self.prob.test_func([0.6, 0.1, 0.1]), 1.5)

    def test_lower_bound_vector(self):
        """
        Test that setting lower bounds work as expected for vector functions.
        """
        x = SpatialCoordinate(self.mesh)
        self.prob.to_bound = as_tensor([Function(self.V).interpolate(x[0]),
                                        Function(self.V).interpolate(1-x[0])])
        self.prob.test_func = self.prob.to_bound + as_tensor([1, 1])

        self.assertAlmostEqual(self.prob.test_func[0]([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func[1]([0.1, 0.1, 0.1]), 1.9)

        self.assertAlmostEqual(self.prob.test_func[0]([0.6, 0.1, 0.1]), 1.6)
        self.assertAlmostEqual(self.prob.test_func[1]([0.6, 0.1, 0.1]), 1.4)

        self.prob.bound('to_bound', lower=0.5)

        self.assertAlmostEqual(self.prob.test_func[0]([0.1, 0.1, 0.1]), 1.5)
        self.assertAlmostEqual(self.prob.test_func[1]([0.1, 0.1, 0.1]), 1.9)

        self.assertAlmostEqual(self.prob.test_func[0]([0.6, 0.1, 0.1]), 1.6)
        self.assertAlmostEqual(self.prob.test_func[1]([0.6, 0.1, 0.1]), 1.5)

    def test_upper_bound_vector(self):
        """
        Test that setting upper bounds work as expected for vector functions.
        """
        x = SpatialCoordinate(self.mesh)
        self.prob.to_bound = as_tensor([Function(self.V).interpolate(x[0]),
                                        Function(self.V).interpolate(1-x[0])])
        self.prob.test_func = self.prob.to_bound + as_tensor([1, 1])

        self.assertAlmostEqual(self.prob.test_func[0]([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func[1]([0.1, 0.1, 0.1]), 1.9)

        self.assertAlmostEqual(self.prob.test_func[0]([0.6, 0.1, 0.1]), 1.6)
        self.assertAlmostEqual(self.prob.test_func[1]([0.6, 0.1, 0.1]), 1.4)

        self.prob.bound('to_bound', upper=0.5)

        self.assertAlmostEqual(self.prob.test_func[0]([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func[1]([0.1, 0.1, 0.1]), 1.5)

        self.assertAlmostEqual(self.prob.test_func[0]([0.6, 0.1, 0.1]), 1.5)
        self.assertAlmostEqual(self.prob.test_func[1]([0.6, 0.1, 0.1]), 1.4)

    def test_upper_and_lower_bound_vector(self):
        """
        Test that setting lower and upper bounds work as expected for vector
        functions.
        """
        x = SpatialCoordinate(self.mesh)
        self.prob.to_bound = as_tensor([Function(self.V).interpolate(x[0]),
                                        Function(self.V).interpolate(1-x[0])])
        self.prob.test_func = self.prob.to_bound + as_tensor([1, 1])

        self.assertAlmostEqual(self.prob.test_func[0]([0.1, 0.1, 0.1]), 1.1)
        self.assertAlmostEqual(self.prob.test_func[1]([0.1, 0.1, 0.1]), 1.9)

        self.assertAlmostEqual(self.prob.test_func[0]([0.6, 0.1, 0.1]), 1.6)
        self.assertAlmostEqual(self.prob.test_func[1]([0.6, 0.1, 0.1]), 1.4)

        self.prob.bound('to_bound', lower=0.45, upper=0.55)

        self.assertAlmostEqual(self.prob.test_func[0]([0.1, 0.1, 0.1]), 1.45)
        self.assertAlmostEqual(self.prob.test_func[1]([0.1, 0.1, 0.1]), 1.55)

        self.assertAlmostEqual(self.prob.test_func[0]([0.6, 0.1, 0.1]), 1.55)
        self.assertAlmostEqual(self.prob.test_func[1]([0.6, 0.1, 0.1]), 1.45)


class TestMin(TestCase):
    """
    Tests for the _min method.
    """

    def setUp(self):
        """
        Create a problem.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = problem.Problem(m, V)

    def test_a_lt_b(self):
        """
        Test returns a if a < b.
        """
        val = self.problem._min(1.0, 3.6)
        self.assertAlmostEqual(val, 1.0)

    def test_a_eq_b(self):
        """
        Test returns a if a == b.
        """
        val = self.problem._min(1.5, 1.5)
        self.assertAlmostEqual(val, 1.5)

    def test_a_gt_b(self):
        """
        Test returns b if a > b.
        """
        val = self.problem._min(1.9, 0.1)
        self.assertAlmostEqual(val, 0.1)


class TestMax(TestCase):
    """
    Tests for the _max method.
    """

    def setUp(self):
        """
        Create a problem.
        """
        m = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(m, 'CG', 1)

        self.problem = problem.Problem(m, V)

    def test_a_lt_b(self):
        """
        Test returns b if a < b.
        """
        val = self.problem._max(1.0, 3.6)
        self.assertAlmostEqual(val, 3.6)

    def test_a_eq_b(self):
        """
        Test returns a if a == b.
        """
        val = self.problem._max(1.5, 1.5)
        self.assertAlmostEqual(val, 1.5)

    def test_a_gt_b(self):
        """
        Test returns a if a > b.
        """
        val = self.problem._max(1.9, 0.1)
        self.assertAlmostEqual(val, 1.9)


# pylint: disable=no-self-use
class TestSteadyStateProblem(TestCase):
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


class TestTimeDependantProblem(TestCase):
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


class TestCreateProblemClass(TestCase):
    """
    Tests for thecreate_problem_class_method.
    """

    def test_is_problem(self):
        """
        Test that the returned class is a subclass of Problem.
        """
        klass = problem.create_problem_class()
        self.assertTrue(issubclass(klass, problem.Problem))
        self.assertTrue(issubclass(klass, BoundaryMixin))

    def test_time_dep_false(self):
        """
        Test that the problem does not inherit from TimeMixin if time_dep is
        false.
        """
        klass = problem.create_problem_class(time_dep=False)
        self.assertFalse(issubclass(klass, TimeMixin))

    def test_time_dep_true(self):
        """
        Test that the problem does inherit from TimeMixin if time_dep is
        true.
        """
        klass = problem.create_problem_class(time_dep=True)
        self.assertTrue(issubclass(klass, TimeMixin))

    def test_sh_conductivity_false(self):
        """
        Test that the problem does not inherit from SpitzerHarmMixin if
        sh_conductivity is false.
        """
        klass = problem.create_problem_class(sh_conductivity=False)
        self.assertFalse(issubclass(klass, SpitzerHarmMixin))

    def test_sh_conductivity_true(self):
        """
        Test that the problem does inherit from SpitzerHarmMixin if
        sh_conductivity is true.
        """
        klass = problem.create_problem_class(sh_conductivity=True)
        self.assertTrue(issubclass(klass, SpitzerHarmMixin))

    def test_constant_ionisation_false(self):
        """
        Test that the problem does inherits from NonConstantIonisationSHCMixin
        if constant_ionisation is false.
        """
        klass = problem.create_problem_class(constant_ionisation=False)
        self.assertTrue(issubclass(klass, NonConstantIonisationSHCMixin))

    def test_constant_ionisation_true(self):
        """
        Test that the problem does inherit from ConstantIonisationSHCMixin if
        constant_ionisation is true.
        """
        klass = problem.create_problem_class(constant_ionisation=True)
        self.assertTrue(issubclass(klass, ConstantIonisationSHCMixin))

    def test_limit_flux_false(self):
        """
        Test that the problem does not inherit from FluxLimiterMixin if
        limit_flux is false.
        """
        klass = problem.create_problem_class(limit_flux=False)
        self.assertFalse(issubclass(klass, FluxLimiterMixin))

    def test_limit_flux_true(self):
        """
        Test that the problem does inherit from FluxLimiterMixin if
        limit_flux is true.
        """
        klass = problem.create_problem_class(limit_flux=True)
        self.assertTrue(issubclass(klass, FluxLimiterMixin))

    def test_limit_conductivity_false(self):
        """
        Test that the problem does not inherit from ConductivityLimiterMixin
        if limit_conductivity is false.
        """
        klass = problem.create_problem_class(limit_conductivity=False)
        self.assertFalse(issubclass(klass, ConductivityLimiterMixin))

    def test_limit_conductivity_true(self):
        """
        Test that the problem does inherit from ConductivityLimiterMixin
        if limit_conductivity is true.
        """
        klass = problem.create_problem_class(limit_conductivity=True)
        self.assertTrue(issubclass(klass, ConductivityLimiterMixin))

    def test_mix(self):
        """
        Test that a mix of settings has all the required functionality.
        """
        klass = problem.create_problem_class(time_dep=True,
                                             sh_conductivity=True,
                                             constant_ionisation=False,
                                             limit_flux=False,
                                             limit_conductivity=True)
        self.assertTrue(issubclass(klass, TimeMixin))
        self.assertTrue(issubclass(klass, SpitzerHarmMixin))
        self.assertTrue(issubclass(klass, NonConstantIonisationSHCMixin))
        self.assertFalse(issubclass(klass, FluxLimiterMixin))
        self.assertTrue(issubclass(klass, ConductivityLimiterMixin))
