"""

"""

from firedrake import Constant, DirichletBC, FacetNormal, dot, ds, grad, replace


from problem import Problem


class BoundaryMixin:

    # Variables that must be present for the mixin.
    mesh = None
    V = None
    v = None
    K = None
    T = None
    a = None
    L = None

    def __init__(self):
        super().__init__()

        self.bcs = []
        self.R = Constant(0)
        self.b = Constant(0)

        self.a += self.R
        self.L += self.b

    def _update_boundaries(self, R=None, b=None):
        if b is not None:
            replace(self.L, {self.b: b})
            self.b = b

        if R is not None:
            replace(self.a, {self.R: R})
            self.R = R

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
            b = self.b + sum(integrand*ds(d) for d in domain)
        except TypeError:
            b = self.b + integrand*ds(domain)

        self._update_boundaries(b=b)
