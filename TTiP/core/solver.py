"""
This file holds the solver class which is used to run the FEM solve.
"""
from firedrake import (H1, File, NonlinearVariationalProblem,
                       NonlinearVariationalSolver)

from TTiP.core.iteration_method import IterationMethod
from TTiP.problem_mixins.boundaries_mixin import BoundaryMixin
from TTiP.problem_mixins.time_mixin import TimeMixin


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

    def solve(self, file_path='ttip_result/solution.pvd',
              method='BackwardEuler', **kwargs):
        """
        Setup and solve the nonlinear problem.
        Save value to file given.
        Any additional keyword arguments are passed to the iteration method.

        Args:
            file_path (string, optional):
                The path to save the pvd file to.
                vtk files will be generated in the same directory as the pvd.
                It is recommended that this is a separate drectory per run.
                Defaults to 'TTiP_result/solution.pvd'.
            method (string, optional):
                If not steady state, this is used to define the method for
                time iterations. Defaults to 'BackwardEuler'.
        """
        F = self.problem.a - self.problem.L
        steady_state = self.is_steady_state()

        if not steady_state:
            iter_method = IterationMethod(self.problem)
            F = iter_method.update(F, method, **kwargs)
            F = self.problem.approx_delT(F)

        if isinstance(self.problem, BoundaryMixin):
            var_prob = NonlinearVariationalProblem(
                F, self.u, bcs=self.problem.bcs)
        else:
            var_prob = NonlinearVariationalProblem(
                F, self.u)
        solver = NonlinearVariationalSolver(problem=var_prob,
                                            solver_parameters=self.params)

        outfile = File(file_path)
        outfile.write(self.u, target_degree=1, target_continuity=H1)

        if steady_state:
            solver.solve()
            outfile.write(self.u,
                          target_degree=1,
                          target_continuity=H1)
        else:
            self.problem.T_.assign(self.u)
            last_perc = 0
            for i in range(self.problem.steps):
                solver.solve()

                perc = int(100 * (i + 1) / self.problem.steps)
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
