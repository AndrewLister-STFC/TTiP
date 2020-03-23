"""
This file is used to test the solve.
"""

import time

from scipy.constants import e, pi

from firedrake import BoxMesh, Constant, FunctionSpace, SpatialCoordinate, sin, Function
from TTiP.problem import (SteadyStateProblem,
                          TimeDependantProblem)
from TTiP.solver import Solver

extent = [40e-6, 40e-6, 40e-6]
mesh = BoxMesh(20, 20, 20, *extent)
V = FunctionSpace(mesh, 'CG', 1)
print(V.dim())

problem = TimeDependantProblem(mesh=mesh, V=V)
problem.set_timescale(dt=1e-12, steps=100)
problem.add_boundary('dirichlet', g=100, domain=[1, 2, 3, 4, 5, 6])
C = Constant(1.1e27)*1.5*e
problem.set_C(C)

x = SpatialCoordinate(mesh)
val = 1
for pos, length in zip(x, extent):
    val *= sin(pos/length*pi)**2
S = Function(V).interpolate(1e9*val)
problem.set_S(S)

x = SpatialCoordinate(mesh)
val = 1
for pos, length in zip(x, extent):
    val *= sin(2*pos/length*pi)
problem.T_.interpolate(100 + 1000**val)
problem.T.assign(problem.T_)

print('Solving')
solver = Solver(problem)

solver.solve()

time.sleep(1)
