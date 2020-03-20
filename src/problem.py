from firedrake import Constant, Function, TestFunction, dot, dx, grad

from mixins.boundaries import BoundaryMixin
from mixins.time import TimeMixin

class Problem:

    def __init__(self, mesh, V):
        """
        Initialiser for Problem.

        Args:
            V (firedrake.FunctionSpace):
                The function space to define the solution on.
        """
        # Store the function space details.
        self.mesh = mesh
        self.V = V

        # Initialise functions for problem.
        self.v = TestFunction(V)
        self.T_ = Function(V)
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
    pass

class TimeDependant(TimeMixin, BoundaryMixin, Problem):
    pass