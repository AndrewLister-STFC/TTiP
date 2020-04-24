"""
Tests for the solver.py file.
"""
import os
import unittest
from tempfile import TemporaryDirectory

import numpy as np

from firedrake import (Constant, FunctionSpace, SpatialCoordinate,
                       UnitCubeMesh, UnitIntervalMesh, pi, sin)

from TTiP.core.problem import SteadyStateProblem, TimeDependantProblem
from TTiP.core.solver import Solver


# pylint: disable=protected-access
class TestSolve(unittest.TestCase):
    """
    Tests for the solve method.
    """

    def setUp(self):
        """
        Setup the mesh and function space.
        """
        self.m = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.m, 'CG', 1)
        self.out_dir = TemporaryDirectory()

    def tearDown(self):
        self.out_dir.cleanup()

    def test_creates_files_steady(self):
        """
        Test that the solve method creates the expected files for a steady
        state problem.
        """
        prob = SteadyStateProblem(mesh=self.m, V=self.V)
        file_path = os.path.join(self.out_dir.name, 'out.pvd')

        prob._update_func('K', Constant(1))
        prob.set_S(Constant(0))
        prob.set_no_boundary()

        solver = Solver(prob)
        solver.u.assign(10)
        solver.solve(file_path=file_path, method='BackwardEuler')

        flist = os.listdir(self.out_dir.name)
        self.assertEqual(len(flist), 3)
        self.assertIn('out.pvd', flist)
        self.assertIn('out_0.vtu', flist)
        self.assertIn('out_1.vtu', flist)

    def test_creates_files_time_dep(self):
        """
        Test that the solve method creates the expected files for a time
        dependent problem.
        """
        prob = TimeDependantProblem(mesh=self.m, V=self.V)
        file_path = os.path.join(self.out_dir.name, 'out.pvd')

        prob._update_func('K', Constant(1))
        prob.set_S(Constant(0))
        prob.set_no_boundary()

        num_steps = 5
        prob.set_timescale(steps=num_steps, dt=0.1)

        solver = Solver(prob)
        solver.u.assign(10)
        solver.solve(file_path=file_path, method='BackwardEuler')

        flist = os.listdir(self.out_dir.name)

        self.assertEqual(len(flist), num_steps+2)
        self.assertIn('out.pvd', flist)
        for i in range(num_steps):
            self.assertIn('out_{}.vtu'.format(i), flist)

    def test_steady_state_result_uniform(self):
        """
        Test that the solve creates a correct uniform result for a simple
        steady state problem.
        """
        prob = SteadyStateProblem(mesh=self.m, V=self.V)
        file_path = os.path.join(self.out_dir.name, 'out.pvd')

        prob._update_func('K', Constant(1))
        prob.set_S(Constant(0))
        prob.add_boundary('dirichlet', g=10, surface='all')

        solver = Solver(prob)
        solver.u.assign(100)
        solver.solve(file_path=file_path, method='BackwardEuler')

        expected = 10

        coords = [[i/10, j/10, k/10]
                  for i in range(11)
                  for j in range(11)
                  for k in range(11)]

        value = solver.u.at(coords)
        self.assertTrue(np.isclose(value, expected).all())

    def test_time_dependant_result_sine(self):
        """
        Test that the solve creates a correct result for a time
        dependant problem with a sine wave initial value.

        T(x,0) = 10*sin(3*pi*x)
        T(0,t) = T(1,t) = 0

        Analytic solution: T(x, t) = 10*sin(3*pi*x)*exp(-pi*pi*9*t)
        """
        m = UnitIntervalMesh(500)
        V = FunctionSpace(m, 'CG', 2)

        prob = TimeDependantProblem(mesh=m, V=V)
        file_path = os.path.join(self.out_dir.name, 'out.pvd')

        prob.set_C(Constant(1))
        prob._update_func('K', Constant(1))
        prob.set_S(Constant(0))
        prob.set_timescale(steps=100, dt=0.00001)
        prob.add_boundary('dirichlet', g=0, surface='all')

        x = SpatialCoordinate(m)
        prob.T_.interpolate(10*sin(x[0]*pi*3))
        prob.T.assign(prob.T_)

        solver = Solver(prob)

        def analytical(x, t):
            return 10*np.sin(3*np.pi*x) * np.exp(-np.pi*np.pi*9*t)

        coords = np.array([i/10 for i in range(11)])

        t = 0
        for i in range(10):
            t = prob.dt*(i+1)*prob.steps
            solver.solve(file_path=file_path, method='CrankNicolson')
            value = solver.u.at(coords)
            expected = analytical(coords, t)
            print(value)
            print(expected)
            self.assertTrue(np.isclose(value, expected).all())


class TestIsSteadyState(unittest.TestCase):
    """
    Test the is_steady_state method.
    """

    def setUp(self):
        """
        Setup the mesh and function space.
        """
        self.m = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.m, 'CG', 1)

    def test_with_time_mixin_prob_true(self):
        """
        Test that a time dependant problem returns true if no time set.
        """
        prob = TimeDependantProblem(mesh=self.m, V=self.V)
        solver = Solver(prob)
        self.assertTrue(solver.is_steady_state())

    def test_with_time_mixin_prob_false(self):
        """
        Test that the time dependant problem returns false if time set.
        """
        prob = TimeDependantProblem(mesh=self.m, V=self.V)
        prob.set_timescale(dt=1.0, steps=5)
        solver = Solver(prob)
        self.assertFalse(solver.is_steady_state())

    def test_without_time_mixin_prob(self):
        """
        Test that non time dependent problems return true.
        """
        prob = SteadyStateProblem(mesh=self.m, V=self.V)
        solver = Solver(prob)
        self.assertTrue(solver.is_steady_state())
