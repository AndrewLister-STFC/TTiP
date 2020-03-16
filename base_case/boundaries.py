from firedrake import (DirichletBC, FacetNormal, SpatialCoordinate, dot, ds,
                       grad, pi, sin)


def set_initial_value(mesh, T, extent):
    """
    Setup T to hold the initial value for the problem.

    mesh: Mesh, The mesh to define the function for
    T: Function, The function to define the initial value on
    extent: list<float>, The length of each side of the mesh (assumes rect)
    """
    x = SpatialCoordinate(mesh)
    val = 1
    for pos, length in zip(x, extent):
        val *= sin(2*pos/length*pi)
    T.interpolate(100 + 1000**val)


def create_robin_bounds(mesh, T, v, k, alpha, g):
    """
    Create the Robin boundary conditions:
    alpha u + dot(grad(u), n) = g

    mesh: Mesh, The mesh to define the bound for
    T: Function, The function to be calculated
    v: Function, The test function
    k: Function, The conductivity of the problem
    alpha: float, Used in above formula
    g: float, Used in above formula

    Returns: bcs, R and b, the defining functions of the bound
    Type: list<DirichletBC>, Function, Function
    """
    bcs = []
    R = k*alpha*v*T*ds
    b = k*v*g*ds

    return bcs, R, b


def create_dirichlet_bounds(mesh, V, T, v, k, g, boundary=[1, 2, 3, 4, 5, 6]):
    """
    Create the dirichlet boundary conditions:
    u = g on boundary

    mesh: Mesh, The mesh to define the bound for
    V: FunctionSpace, The function space for the boundary
    T: Function, The function to be calculated
    v: Function, The test function
    k: Function, The conductivity of the problem
    g: float, Used in above formula

    Returns: bcs, R and b, the defining functions of the bound
    Type: list<DirichletBC>, Function, Function
    """
    norm = FacetNormal(mesh)

    bcs = [DirichletBC(V, g, boundary)]
    R = 0
    b = k*v*dot(grad(T), norm)*ds

    return bcs, R, b
