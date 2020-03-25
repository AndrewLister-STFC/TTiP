"""
This file is used to test the solve.
"""

import time

from scipy.constants import e, pi

from firedrake import (BoxMesh, Constant, Function, FunctionSpace,
                       SpatialCoordinate, sin)
from TTiP.core.problem import SteadyStateProblem, TimeDependantProblem
from TTiP.core.solver import Solver


def main():
    # =========================================================================
    # ===== CREATE MESH =======================================================
    # =========================================================================
    extent = [40e-6, 40e-6, 40e-6]
    mesh = BoxMesh(20, 20, 20, *extent)

    # =========================================================================
    # ===== CREATE FUNCTION SPACE =============================================
    # =========================================================================
    V = FunctionSpace(mesh, 'CG', 1)

    # =========================================================================
    # ===== SETUP PROBLEM =====================================================
    # =========================================================================
    problem = TimeDependantProblem(mesh=mesh, V=V)

    # =========================================================================
    # ===== TIME ==============================================================
    # =========================================================================
    problem.set_timescale(dt=1e-13, steps=100)

    # =========================================================================
    # ===== PARAMETERS ========================================================
    # =========================================================================
    C = Constant(1.1e27)*1.5*e
    problem.set_C(C)

    # =========================================================================
    # ===== SOURCES ===========================================================
    # =========================================================================
    x = SpatialCoordinate(mesh)
    val = 1
    for pos, length in zip(x, extent):
        val *= sin(pos/length*pi)**2
    S = Function(V).interpolate(1e9*val)
    problem.set_S(S)

    # =========================================================================
    # ===== BOUNDARIES ========================================================
    # =========================================================================
    problem.add_boundary('dirichlet', g=100, domain=[1, 2, 3, 4, 5, 6])

    # =========================================================================
    # ===== INITIAL VALUE =====================================================
    # =========================================================================
    x = SpatialCoordinate(mesh)
    val = 1
    for pos, length in zip(x, extent):
        val *= sin(2*pos/length*pi)
    problem.T_.interpolate(100 + 1000*val)
    problem.T.assign(problem.T_)

    # =========================================================================
    # ===== SOLVE =============================================================
    # =========================================================================
    print('Solving')
    solver = Solver(problem)

    solver.solve(method='Theta', theta=0.5)


if __name__ == '__main__':
    main()
