"""
This file stores the base problem and any created by adding mixins.
"""
from firedrake import Function, TestFunction, dot, dx, grad


from TTiP.mixins.boundaries import BoundaryMixin
from TTiP.mixins.time import TimeMixin


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
        a (firedrake.Function):
            A function used to combine parts including T and v.
            Used to solve the problem of finding a - L = 0.
        L (firedrake.Function):
            A function used to combine parts not in 'a' (see above).
    """

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
        self.T = Function(V)
        self.S = Function(V)
        self.K = Function(V)

        self.a = self._A()
        self.L = self._f()

    def _A(self):
        """
        Create a stiffness matrix section.

        Returns:
            Function: A complete stiffness matrix section.
        """
        return self.K*dot(grad(self.T), grad(self.v))*dx

    def _f(self):
        """
        Create a source function section.

        Returns:
            Function: A complete source function section.
        """
        return self.S*self.v*dx


class SteadyState(BoundaryMixin, Problem):
    """
    A steady state problem with no time dependance.
    This solves the problem where dT/dt=0.
    """
    pass


class TimeDependant(TimeMixin, BoundaryMixin, Problem):
    """
    A full time dependant problem.
    This includes all terms.
    """
    pass
