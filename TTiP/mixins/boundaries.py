"""
Contains the BoundaryMixin class for extending problems.
"""

from firedrake import (Constant, DirichletBC, FacetNormal, dot, ds, grad,
                       replace)


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
        T (firedrake.Function):
            The trial function for the problem.
        v (firedrake.Function):
            The test function for the problem.
        K (firedrake.Function):
            A function holding the conductivity for the problem. 
        a (firedrake.Function):
            The section containing the combination of terms involving both T
            and v.
        L (firedrake.Function):
            The section containing the combination of terms not in a.

    Attributes:
        bcs (list<firedrake.DirichletBC>):
            A list of any dirichlet contitions that are defined.
            These can't be worked into the variational problem directly.
        R (firedrake.Function):
            A function holding parts of the bounds containing both T and v.
            e.g. K alpha T v ds (robin bound)
        b (firedrake.Function):
            A function holding parts of the bounds that don't contain both T
            and v.
            e.g. K v g ds (robin bound)
    """

    # Variables that must be present for the mixin.
    # These will be replaced by the init in te class this is mixed into.
    mesh = None
    V = None
    T = None
    v = None
    K = None
    a = None
    L = None

    def __init__(self):
        """
        Initialiser for BoundaryMixin.

        Adds R and b to a and L respectively.
        Also creates empty bcs list.
        """
        super().__init__()

        self.bcs = []
        self.R = Constant(0)
        self.b = Constant(0)

        self.a += self.R
        self.L += self.b

    def _update_boundaries(self, R=None, b=None):
        """
        Update the values of the boundaries in the combined function if given.

        Args:
            R (firedrake.Function, optional):
                The new value for R. Defaults to None.
            b (firedrake.Function, optional):
                The new value for b. Defaults to None.
        """
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

        integrand = -self.K*self.v*dot(grad(self.T), norm)
        try:
            R = self.R + sum(integrand*ds(d) for d in domain)
        except TypeError:
            R = self.R + integrand*ds(domain)

        self._update_boundaries(R=R)
