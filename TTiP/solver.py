"""
This file holds the solver class which is used to run the FEM solve.
"""
from datetime import datetime

from firedrake import (H1, File, NonlinearVariationalProblem,
                       NonlinearVariationalSolver)
from TTiP.mixins.time import TimeMixin
from TTiP.mixins.boundaries import BoundaryMixin


class Solver:
    """
    A class for the solver.

    Attributes:
        problem (TTiP.problem.Problem (or subclass)):
            The problem to solve.
        u (firedrake.Function):
            The variable to solve for in the problem.
        params (dict):
            The parameters passed to the solver.
    """

    def __init__(self, problem):
        """
        Initialise the Solver.

        Args:
            problem (TTiP.problem.Problem):
                The problem to solve.
        """
        self.problem = problem
        self.u = problem.T

        self.params = {
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
            'snes_max_it': 100}

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
        F = self.problem.a - self.problem.L

        if isinstance(self.problem, BoundaryMixin):
            var_prob = NonlinearVariationalProblem(
                F, self.u, bcs=self.problem.bcs)
        else:
            var_prob = NonlinearVariationalProblem(
                F, self.u)
        solver = NonlinearVariationalSolver(problem=var_prob,
                                            solver_parameters=self.params)


        steady_state = True
        if isinstance(self.problem, TimeMixin):
            steady_state = self.problem.steady_state

        timestamp = datetime.now().strftime("%d-%b-%Y-%H-%M-%S")
        outfile = File(f'{timestamp}/from_TTiP.pvd')
        outfile.write(self.u, target_degree=1, target_continuity=H1)

        if steady_state:
            solver.solve()
            outfile.write(self.u,
                          target_degree=1,
                          target_continuity=H1)
        else:
            self.u.assign(self.problem.T_)
            last_perc = 0
            for i in range(self.problem.steps):
                solver.solve()

                perc = int(100*(i+1)/self.problem.steps)
                if perc > last_perc:
                    print(f'{perc}%')
                    last_perc = perc

                self.problem.T_.assign(self.u)
                outfile.write(self.u,
                              target_degree=1,
                              target_continuity=H1)
