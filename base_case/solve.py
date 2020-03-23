# import matplotlib.pyplot as plt

from datetime import datetime
import time

from boundaries import (create_dirichlet_bounds, create_robin_bounds,  # NOQA
                        set_initial_value)
from firedrake import (H1, Constant, File, Function, FunctionSpace,
                       NonlinearVariationalProblem, NonlinearVariationalSolver,
                       BoxMesh, TestFunction, dot, dx, grad)
from parameters import create_conductivity, create_heat_capacity, create_S

SOLVE_PARAMS = {
    'snes_type': 'newtonls',
    'mat_type': 'matfree',
    'ksp_type': 'gmres',  # 'preonly',
    'pc_type': 'python',
    'pc_python_type': 'firedrake.AssembledPC',
    'assembled_pc_type': 'hypre',  # 'lu',
    'assembled_pc_factor_mat_solver_type': 'mumps',
    # 'snes_monitor': None,
    # 'snes_view': None,
    # 'ksp_monitor_true_residual': None,
    # 'snes_converged_reason': None,
    # 'ksp_converged_reason': None,
    'snes_linesearch_type': 'l2',
    'snes_linesearch_maxstep': 1.0,
    'snes_atol': 1e-6,
    'snes_rtol': 0,
    'snes_stol': 1e-16,
    'snes_max_L_solve_fail': 10,
    'snes_max_it': 100
}

STEADY = True


def run(steady=False):
    """
    solve CdT/dt = S + div(k*grad(T))
    => C*v*(dT/dt)/k*dx - S*v/k*dx + grad(v)*grad(T)*dx = v*dot(grad(T), n)*ds
    """
    steps = 250
    dt = 1e-10
    timescale = (0, steps*dt)
    if steady:
        print('Running steady state.')
    else:
        print(f'Running with time step {dt:.2g}s on time interval: '
              f'{timescale[0]:.2g}s - {timescale[1]:.2g}s')
    dt_invc = Constant(1/dt)
    extent = [40e-6, 40e-6, 40e-6]
    mesh = BoxMesh(20, 20, 20, *extent)

    V = FunctionSpace(mesh, 'CG', 1)
    print(V.dim())

    T = Function(V)  # temperature at time i+1 (electron for now)
    T_ = Function(V)  # temperature at time i
    v = TestFunction(V)  # test function

    S = create_S(mesh, V, extent)
    C = create_heat_capacity(mesh, V, extent)
    k = create_conductivity(mesh, V, T)

    set_initial_value(mesh, T_, extent)

    # Mass matrix section
    M = C*T*dt_invc*v*dx
    M_ = C*T_*dt_invc*v*dx
    # Stiffness matrix section
    A = k*dot(grad(T), grad(v))*dx
    # function section
    f = S*v*dx
    # boundaries
    bcs, R, b = create_dirichlet_bounds(mesh, V, T, v, k,
                                        g=100,
                                        boundary=[1, 2, 3, 4, 5, 6])
    # bcs += create_dirichlet_bounds(mesh, V, T, v, k, 500, [6])[0]
    # bcs, R, b = create_robin_bounds(mesh, T, v, k, 1e8/(100), 1e8)

    if steady:
        steps = 1
        a = A + R
        L = f + b
    else:
        a = M + A + R
        L = M_ + f + b

    prob = NonlinearVariationalProblem(a - L, T, bcs=bcs)
    solver = NonlinearVariationalSolver(prob, solver_parameters=SOLVE_PARAMS)

    T.assign(T_)

    timestamp = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")
    outfile = File(f'{timestamp}/first_output.pvd')
    outfile.write(T_, target_degree=1, target_continuity=H1)
    last_perc = 0
    for i in range(steps):
        solver.solve()

        perc = int(100*(i+1)/steps)
        if perc > last_perc:
            print(f'{perc}%')
            last_perc = perc

        T_.assign(T)
        outfile.write(T_, target_degree=1, target_continuity=H1)


if __name__ == '__main__':
    start = time.time()
    run(STEADY)
    print(f'Finished: {time.time()-start}s')
