"""
This file stores the base problem and any created by adding mixins.
"""
from firedrake import (Function, TestFunction, as_tensor, dot, dx, grad,
                       replace, sqrt)
from scipy.constants import e, m_e
from ufl import Form, Integral
from ufl.core.expr import Expr

from TTiP.problem_mixins.boundaries_mixin import BoundaryMixin
from TTiP.problem_mixins.conductivity_mixin import SpitzerHarmMixin
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
            A function to hold v_th.
        a (firedrake.Function):
            A function used to combine parts including T and v.
            Used to solve the problem of finding a - L = 0.
        L (firedrake.Function):
            A function used to combine parts not in 'a' (see above).
    """
    # pylint: disable=too-few-public-methods

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
        # Store the function space details.
        self.mesh = mesh
        self.V = V

        # Initialise functions for problem.
        self.v = TestFunction(V)
        self.T = Function(V, name='T')
        self.S = Function(V, name='S')

        self.K = Function(V, name='K')

        self.q = self.K * grad(self.T)
        self.v_th = sqrt(3 * e * self.T / m_e)

        self.a = self._A()
        self.L = self._f()

    def set_S(self, S):
        """
        Replace S in all formulas (namely L).

        Args:
            S (Function):
                The new value for S.
        """
        self._update_func('S', S)

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

    def bound(self, name, lower=None, upper=None):
        """
        Impose bounds on a function.
        This replaces a function with a bounded version.

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


class SteadyStateProblem(SpitzerHarmMixin, BoundaryMixin, Problem):
    """
    A steady state problem with no time dependance.
    This solves the problem where dT/dt=0.
    """


class TimeDependantProblem(SpitzerHarmMixin, TimeMixin, BoundaryMixin,
                           Problem):
    """
    A full time dependant problem.
    This includes all terms.
    """
