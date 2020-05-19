"""
This file stores the base problem and any created by adding mixins.
"""
from firedrake import (Function, TestFunction, as_tensor, dot, dx, grad,
                       replace, sqrt)
from scipy.constants import e, m_e
from ufl import Form, Integral
from ufl.core.expr import Expr

from TTiP.problem_mixins.boundaries_mixin import BoundaryMixin
from TTiP.problem_mixins.conductivity_mixin import (ConductivityLimiterMixin,
                                                    SpitzerHarmMixin)
from TTiP.problem_mixins.flux_limit_mixin import FluxLimiterMixin
from TTiP.problem_mixins.specific_heat_capacity_mixin import (
    ConstantIonisationSHCMixin, NonConstantIonisationSHCMixin)
from TTiP.problem_mixins.time_mixin import TimeMixin


class Problem:
    """
    A base class for problems.
    To use this, inherit from this and combine mixins.

    Attributes:
        mesh (firedrake.Mesh):
            The mesh that the problem is defined on.
        V (firedrake.FunctionSpace):
            The FunctionSpace to define the solution on.
        v (firedrake.TestFunction):
            The test function for the problem.
        T (firedrake.Function):
            A function to hold the result. This is usually a trial function
            however in this case we expect the problem to be non-linear, in
            which case firedrake uses a Function.
        S (firedrake.Function):
            A function to hold any sources. This may be moved to a mixin.
        K (firedrake.Function):
            A function to hold the heat conductivity. This defines how the heat
            flows through the mesh.
        q (firedrake.Function):
            A function to hold the heat flux (K*grad(T)).
        v_th (firedrake.Function):
            A function to hold v_th (thermal velocity?).
        a (firedrake.Function):
            A function used to combine parts including T and v.
            Used to solve the problem of finding a - L = 0.
        L (firedrake.Function):
            A function used to combine parts not in 'a' (see above).
    """
    # pylint: disable=too-few-public-methods, no-member

    def __init__(self, mesh, V):
        """
        Initialiser for Problem.
        Sets up the a and L variables that are used throughout the mixins.

        Args:
            mesh (firedrake.Mesh):
                The mesh that the problem is defined on.
            V (firedrake.FunctionSpace):
                The function space to define the solution on.
        """
        self._functions = []

        # Store the function space details.
        self.mesh = mesh
        self.V = V

        # Initialise functions for problem.
        self.v = TestFunction(V)

        self._add_function('T')
        self._add_function('S')
        self._add_function('K')
        self._add_function('q')
        self._add_function('v_th')
        self._add_function('ionisation')
        self._add_function('atomic_number')
        self._add_function('a')
        self._add_function('L')

        self.q = self.K * grad(self.T)
        self.v_th = sqrt(3 * e * self.T / m_e)
        self.ionisation = self._ionisation()

        self.a = self._A()
        self.L = self._f()

    def set_function(self, name, value):
        """
        Replace named function in all formulas.

        Args:
            name (str):
                The name of the function to replace.
            value (Function):
                The value to replace the named function with.
        """
        if name not in self._functions:
            raise AttributeError('Could not set "{}"'.format(name))
        self._update_func(name, value)

    def _A(self):
        """
        Create a stiffness matrix section.

        Returns:
            Function: A complete stiffness matrix section.
        """
        return dot(self.q, grad(self.v)) * dx

    def _f(self):
        """
        Create a source function section.

        Returns:
            Function: A complete source function section.
        """
        return self.S * self.v * dx

    def _ionisation(self):
        """
        Create the ionisation energy term.

        Returns:
            Function: The ionisation term.
        """
        T_prime = self.atomic_number**(-4 / 3) * self.T
        tmp = self.atomic_number * T_prime * (2.2 + T_prime)
        return tmp / (1.1 + T_prime)**2

    def _update_func(self, name, val):
        """
        Utility function to update a function in the main attributes.

        Args:
            name (str): The name of the function to update.
            val (Function): The new value for the function.

        Raises:
            AttributeError: If name is not in self.
        """
        if not hasattr(self, name):
            raise AttributeError('Cannot update {}'.format(name))

        attrs = vars(self).copy()
        old_val = getattr(self, name)
        for attr_name, attr_val in attrs.items():
            if isinstance(attr_val, (Form, Integral, Expr)):
                updated_val = replace(attr_val, {old_val: val})
                setattr(self, attr_name, updated_val)

    def _add_function(self, name):
        """
        Ensure the problem has required attribute.
        If attribute already exists, do nothing.
        Otherwise create a new function to hold it and add a setter method.

        Args:
            name (str): The name of the attribute to create.
        """
        if name in self._functions:
            return

        if hasattr(self, name):
            raise AttributeError('"{}" already exists and is not a function.'
                                 ''.format(name))

        f = Function(self.V, name=name)
        setattr(self, name, f)

        self._functions.append(name)

    def bound(self, name, lower=None, upper=None):
        """
        Impose bounds on a function.
        This replaces a function with a bounded version in all formulas.
        Note: This does not change the variable itself.

        For multi-dimensional functions this will apply bounds elementwise.

        Args:
            name (str): The name of the attribute to.
            lower (Function, optional): A lower bound. Defaults to None.
            upper (Function, optional): An upper bound. Defaults to None.

        Raises:
            AttributeError: Attribute does not exist.
        """
        if not hasattr(self, name):
            raise AttributeError('No variable: {}'.format(name))

        if lower is None and upper is None:
            return

        val = getattr(self, name)
        unbounded = val

        if lower is not None:
            if val.ufl_shape:
                val = as_tensor([self._max(v, lower) for v in val])
            else:
                val = self._max(val, lower)

        if upper is not None:
            if val.ufl_shape:
                val = as_tensor([self._min(v, upper) for v in val])
            else:
                val = self._min(val, upper)

        self._update_func(name, val)
        setattr(self, name, unbounded)

    def _min(self, a, b):
        """
        Return the minimum of a and b.

        Args:
            a (Function or num): The first value.
            b (Function or num): The second value.

        Returns:
            Function or num: The minimum of a and b.
        """
        return 0.5 * (a + b - abs(a - b))

    def _max(self, a, b):
        """
        Return the maximum of a and b.

        Args:
            a (Function or num): The first value.
            b (Function or num): The second value.

        Returns:
            Function or num: The maximum of a and b.
        """
        return 0.5 * (a + b + abs(a - b))


class SteadyStateProblem(ConductivityLimiterMixin,
                         FluxLimiterMixin,
                         SpitzerHarmMixin,
                         ConstantIonisationSHCMixin,
                         BoundaryMixin,
                         Problem):
    """
    A steady state problem with no time dependance.
    This solves the problem where dT/dt=0.
    """


class TimeDependantProblem(ConductivityLimiterMixin,
                           FluxLimiterMixin,
                           SpitzerHarmMixin,
                           TimeMixin,
                           ConstantIonisationSHCMixin,
                           BoundaryMixin,
                           Problem):
    """
    A full time dependant problem.
    This includes all terms.
    """


def create_problem_class(time_dep=False,
                         sh_conductivity=True,
                         constant_ionisation=True,
                         limit_flux=True,
                         limit_conductivity=True):
    """
    Create a problem class using a subset of available functionality.

    Args:
        time_dep (bool, optional):
            Whether the problem will have time dependency.
            Defaults to False.
        sh_conductivity (bool, optional):
            Whether to use spitzer harm conductivity for the problem.
            Defaults to True.
        constant_ionisation (bool, optional):
            Whether to use constant or non-constant ionisation.
            Defaults to True.
        limit_flux (bool, optional):
            Whether to enable flux limiting on the problem.
            Defaults to True.
        limit_conductivity (bool, optional):
            Whether to impose a lower physical bound on the conductivity.
            Defaults to True.

    Returns:
        class: A problem class with the required functionality.
    """

    dependancies = [BoundaryMixin, Problem]

    if time_dep:
        dependancies.insert(0, TimeMixin)
    if sh_conductivity:
        dependancies.insert(0, SpitzerHarmMixin)
    if constant_ionisation:
        dependancies.insert(0, ConstantIonisationSHCMixin)
    else:
        dependancies.insert(0, NonConstantIonisationSHCMixin)
    if limit_flux:
        dependancies.insert(0, FluxLimiterMixin)
    if limit_conductivity:
        dependancies.insert(0, ConductivityLimiterMixin)

    class CustomProblem(*dependancies):
        """
        A custom problem class using the following mixins:
        - {}
        """.format('\n- '.join([d.__name__ for d in dependancies]))

    return CustomProblem
