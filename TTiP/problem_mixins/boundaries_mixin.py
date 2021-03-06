"""
Contains the BoundaryMixin class for extending problems.
"""

from firedrake import Constant, DirichletBC, FacetNormal, dot, ds


class BoundaryMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow boundary values by adding the
    `K dot(grad(T), n) ds` term.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(BoundaryMixin, Problem):
           pass

    Required Attributes (for mixin):
        mesh (firedrake.Mesh):
            The mesh that the problem is defined for.
        V (firedrake.FunctionSpace):
            A function space on which functions will be defined.
        v (firedrake.Function):
            The test function for the problem.

    Attributes:
        T (firedrake.Function):
            The trial function for the problem.
        q (firedrake.Function):
            A function holding the heat flux.
        a (firedrake.Function):
            The section containing the combination of terms involving both T
            and v.
        L (firedrake.Function):
            The section containing the combination of terms not in a.
        bcs (list<firedrake.DirichletBC>):
            A list of any dirichlet contitions that are defined.
            These can't be worked into the variational problem directly.
        _has_boundary (bool);
            Flag that is set to true when a boundary has been set.
    """
    # pylint: disable=no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for BoundaryMixin.

        Boundaries are added in the specific funcs.
        There is no way to remove a boundary.
        Also creates empty bcs list.
        """
        super().__init__(*args, **kwargs)

        self._add_function('T')
        self._add_function('q')
        self._add_function('a')
        self._add_function('L')

        self.bcs = []
        self._has_boundary = None

    def add_boundary(self, boundary_type, **kwargs):
        """
        Generic method for adding boundaries to the problem.

        To view documentation for boundary types, see the appropriate function.

        Args:
            boundary_type (string):
                The name of the boundary condition:
                    - "dirichlet"
                    - "robin"
                    - "neuman" (in progress)
                These can be given in full, or as shortened names (e.g. "dir")

        Raises:
            ValueError: When the boundary is not in the supported names list.
        """
        dispatcher = {'dirichlet': self.add_dirichlet,
                      'robin': self.add_robin}
        for name, func in dispatcher.items():
            if name.startswith(boundary_type):
                func(**kwargs)
                break
        else:
            raise ValueError('{} boundaries are not supported. Supported '
                             'boundaries are: {}.'.format(
                                 boundary_type, ', '.join(dispatcher.keys())))

    def add_dirichlet(self, g, surface):
        """
        Adds dirichlet boundary conditions to the problem.

        Args:
            g (Function, int, or float):
                The function to apply on the boundary.
            surface (int or list of int):
                The index of the boundary to apply the condition to.
        """
        # Explicitly check against False as None should not be caught here.
        if self._has_boundary is False:
            raise AttributeError('Cannot add boundary after declaring that '
                                 'there are no boundaries')
        norm = FacetNormal(self.mesh)

        if isinstance(g, (float, int)):
            g = Constant(g)

        integrand = -1 * self.v * dot(self.q, norm)

        if surface == 'all':
            dbc = DirichletBC(V=self.V, g=g, sub_domain="on_boundary")
            self.a += integrand * ds
        else:
            dbc = DirichletBC(V=self.V, g=g, sub_domain=surface)
            try:
                self.a += sum(integrand * ds(s) for s in surface)
            except TypeError:
                self.a += integrand * ds(surface)

        self.bcs.append(dbc)
        self._has_boundary = True

    def add_robin(self, alpha, g, surface):
        """
        Adds robin boundary conditions to the problem.

        The Robin condition is a mixed codition and is defined by:
            dot(grad(T), n) = g - alpha*T

        Args:
            g (Function, int, or float):
                The function to apply on the boundary as per the above formula.
            alpha (Function, int, or float):
                The function to apply on the boundary as per the above formula.
            surface (int or list of int):
                The index of the boundary to apply the condition to.
        """
        # Explicitly check against False as None should not be caught here.
        if self._has_boundary is False:
            raise AttributeError('Cannot add boundary after declaring that '
                                 'there are no boundaries')

        if isinstance(g, (float, int)):
            g = Constant(g)
        if isinstance(alpha, (float, int)):
            alpha = Constant(alpha)

        a_integrand = alpha * self.v * self.T
        L_integrand = self.v * g

        if surface == 'all':
            self.a += a_integrand * ds
            self.L += L_integrand * ds
        else:
            try:
                self.a += sum(a_integrand * ds(s) for s in surface)
                self.L += sum(L_integrand * ds(s) for s in surface)
            except TypeError:
                self.a += a_integrand * ds(surface)
                self.L += L_integrand * ds(surface)

        self._has_boundary = True

    def set_no_boundary(self):
        """
        Declare that the problem will have no boundaries.

        Raises:
            AttributeError: If boundaries have already been added.
        """
        # Explicitly check for True to be consistent with other method.
        if self._has_boundary is True:
            raise AttributeError('Cannot set no boundary after boundaries have'
                                 ' been set')

        norm = FacetNormal(self.mesh)
        self.a += -1 * self.v * dot(self.q, norm) * ds
        self._has_boundary = False
