"""
This file holds the solver class which is used to run the FEM solve..
"""
from firedrake import (Constant, DirichletBC, FacetNormal, Function,
                       NonlinearVariationalProblem, NonlinearVariationalSolver,
                       TestFunction, dot, ds, dx, grad)


class Solver:
    """
    A class for the solver.

    To use this:
        Define the parameters of the solve
        - C: The heat capacity
        - S: Heat sources/sinks
        - K: The conductivity
        Add any boundary conditions (currently only dirichlet are available)
        Set timescale (Skipping this implicitly defines a steady state problem)
        Call solve
    """

    def __init__(self, mesh, V):
        """
        Initialiser for Solver.

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
        self.C = Constant(1)
        self.S = Constant(1)
        self.K = Constant(1)

        # Initialise params for steady state problem.
        self.steady_state = True

        # Initialise params for time dependent problem.
        self.dt = 1
        self.t_max = 1
        self.dt_inv = Constant(1)

        # Initialise params for boundaries
        self.R = Constant(0)
        self.b = Constant(0)
        self.bcs = []

        # Initialise dict for solver params
        self.params = {}

    def solve(self):
        """
        Setup and solve the nonlinear problem.
        If running steady state, return the result.
        Otherwise, yield each result in turn.

        Returns:
            firedrake.Function:
                Steady state only.
                The Function set to the solution after running the steady state
                solve. (dT/dt = 0)

        Yields:
            firedrake.Function:
                The Function set to the solution at the next timestep.
        """
        F = self._a() - self._L()

        problem = NonlinearVariationalProblem(F, self.T, bcs=self.bcs)
        solver = NonlinearVariationalSolver(problem=problem,
                                            solver_parameters=self.params)

        self.T.assign(self.T_)

        if self.steady_state:
            solver.solve()
            return self.T

        steps = self.t_max*self.dt_inv.dat.data[0]
        for _ in range(steps):
            solver.solve()
            self.T_.assign(self.T)
            yield self.T_

    def add_boundary(self, boundary_type, **kwargs):
        """
        Generic method for adding boundaries to the problem.
        Currently only "dirichlet" boundaries are accepted.

        To view documentation for boundary types, see the appropriate function.

        Args:
            boundary_type (string):
                The name of the boundary condition:
                    - "dirichlet"
                    - "robin" (in progress)
                    - "neuman" (in progress)
                These can be given in full, or as shortened names (e.g. "dir")

        Raises:
            ValueError: When the boundary is not in the supported names list.
        """
        dispatcher = {'dirichlet': self.add_dirichlet}
        for name, func in dispatcher.items():
            if name.startswith(boundary_type):
                func(**kwargs)
                break
        else:
            raise ValueError('{} boundaries are not supported. Supported '
                             'boundaries are: {}.'.format(
                                 boundary_type, ', '.join(dispatcher.keys())))

    def add_dirichlet(self, g, domain):
        """
        Adds dirichlet boundary conditions to the problem.

        Args:
            g (Function, int, or float):
                The function to apply on the boundary.
            domain (int or list of int):
                The index of the boundary to apply the condition to.
        """
        norm = FacetNormal(self.mesh)

        if isinstance(g, [float, int]):
            g = Constant(g)

        dbc = DirichletBC(self.V, g, domain)
        self.bcs.append(dbc)

        integrand = self.K*self.v*dot(grad(self.T), norm)
        try:
            self.b += sum(integrand*ds(d) for d in domain)
        except TypeError:
            self.b += integrand*ds(domain)

    def _a(self):
        """
        Create the bilinear section (a) of the variational problem.

        Returns:
            Function: A complete function containing a.
        """
        A = self._create_A()
        R = self.R
        if self.steady_state:
            return A + R

        M = self._create_M(self.T)
        return M + A + R

    def _L(self):
        """
        Create the linear section (L) of the variational problem.

        Returns:
            Function: A complete function containing L.
        """
        f = self._create_f()
        b = self.b
        if self.steady_state:
            return f + b

        M_ = self._create_M(self.T_)
        return M_ + f + b

    def _create_M(self, T=None):
        """
        Create a mass matrix section in the variable given.
        If T is not given, this will use self.T.

        Args:
            T (Function): The function to go in the mass matrix.

        Returns:
            Function: A complete function containing the mass matrix section.
        """
        return self.C*T*self.v*self.dt_inv*dx

    def _create_A(self):
        """
        Create a stiffness matrix section.

        Returns:
            Function: A complete stiffness matrix section.
        """
        return self.K*dot(grad(self.T), grad(self.v))*dx

    def _create_f(self):
        """
        Create a source function section.

        Returns:
            Function: A complete source function section.
        """
        return self.S*self.v*dx
