from scipy.constants import e, epsilon_0, m_e, pi

from firedrake import Constant, Function, SpatialCoordinate, sin, sqrt


def create_heat_capacity(mesh, V, extent):
    """
    This is the heat capacity term.

    mesh: Mesh, The mesh to define the function for.
    V: FunctionSpace, The function space that the function should be in
    extent: list<float>, The length of each side of the mesh (assumes rect)
    """
    n = create_n(mesh, V, extent)
    return n*1.5*e


def create_conductivity(mesh, V, T):
    """
    This is the conductivity term.
    Here we use the spitzer-harm conductivity.

    mesh: Mesh, The mesh to define the function for.
    V: FunctionSpace, The function space that the function should be in
    T: Function, The temperature of the plasma.
    """
    coulomb_ln = create_coulomb_ln(mesh, V)
    Z = create_Z(mesh, V)

    tmp = 288*pi*sqrt(2)*epsilon_0**2/sqrt(e*m_e)
    tmp = tmp*pow(T, 5/2)/(coulomb_ln*Z)

    return tmp


def create_S(mesh, V, extent):
    """
    This is the source term.

    mesh: Mesh, The mesh to define the function for.
    V: FunctionSpace, The function space that the function should be in
    extent: list<float>, The length of each side of the mesh (assumes rect)
    """
    x = SpatialCoordinate(mesh)
    val = 1
    for pos, length in zip(x, extent):
        val *= sin(pos/length*pi)**2
    return Function(V).interpolate(1e9*val)


def create_n(mesh, V, extent):
    """
    This is the density of the plasma.

    For the first result we will assume this is uniform.

    mesh: Mesh, The mesh to define the function for.
    V: FunctionSpace, The function space that the function should be in
    extent: list<float>, The length of each side of the mesh (assumes rect)
    """
    # x, y = SpatialCoordinate(mesh)
    # n = Function(V).interpolate(...)

    return Constant(1.1e27)


def create_Z(mesh, V):
    """
    Create the Ionization term.

    For the simple case we will assume carbon (~12)

    mesh: Mesh, The mesh to define the function for.
    V: FunctionSpace, The function space that the function should be in
    """
    return Constant(12)


def create_coulomb_ln(mesh, V):
    """
    Create the coulomb logarithm term.

    For the simple case we will assume this is 10

    mesh: Mesh, The mesh to define the function for.
    V: FunctionSpace, The function space that the function should be in
    """
    return Constant(10)
