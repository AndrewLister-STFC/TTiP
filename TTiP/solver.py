"""
This file holds the solver class which is used to run the FEM solve.
"""
from datetime import datetime

from firedrake import (H1, File, NonlinearVariationalProblem,
                       NonlinearVariationalSolver)

from TTiP.iteration_method import IterationMethod
from TTiP.mixins.boundaries import BoundaryMixin
from TTiP.mixins.time import TimeMixin


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

    def solve(self, file_path='TTiP_result/solution.pvd'):
        """
        Setup and solve the nonlinear problem.
        Save value to file given.

        Args:
            file_path (string):
                The path to save the pvd file to.
                vtk files will be generated in the same directory as the pvd.
                It is recommended that this is a separate drectory per run.
        """
        F = self.problem.a - self.problem.L
        steady_state = self.is_steady_state()

        if not steady_state:
            iter_method = IterationMethod(self.problem)
            F = iter_method.update(F, 'BackwardEuler')
            F = self.problem.approx_delT(F)

        if isinstance(self.problem, BoundaryMixin):
            var_prob = NonlinearVariationalProblem(
                F, self.u, bcs=self.problem.bcs)
        else:
            var_prob = NonlinearVariationalProblem(
                F, self.u)
        solver = NonlinearVariationalSolver(problem=var_prob,
                                            solver_parameters=self.params)

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

    def is_steady_state(self):
        """
        Check if the problem is steady state or not.

        Returns:
            bool: Whether the problem is steady state.
        """
        if isinstance(self.problem, TimeMixin):
            return self.problem.steady_state
        return True
