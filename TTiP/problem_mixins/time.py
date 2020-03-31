"""
Contains the TimeMixin class for extending problems.
"""
from firedrake import Constant, Function, dx, replace


class TimeMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow time stepping by adding the dT/dt
    term.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(TimeMixin, Problem):
           pass

    Required Attributes (for mixin):
        V (firedrake.FunctionSpace):
            A function space on which functions will be defined.
        T (firedrake.Function):
            The trial function for the problem.
        v (firedrake.Function):
            The test function for the problem.
        a (firedrake.Function):
            The section containing the combination of terms involving both T
            and v.
        L (firedrake.Function):
            The section containing the combination of terms not in a.

    Attributes:
        T_ (firedrake.Function):
            A function used to hold the previous value for T.
        delT (firedrake.Function):
            A function used as a placeholder for the time derivative.
        C (firedrake.Function):
            A function used to hold the heat capacity of the mesh.
        t_max (float):
            The time to iterate up to.
        dt (float):
            The size of each time step.
        _dt_invc (firedrake.Constant):
            Utility function to pass time step information to firedrake.
        steps (int):
            Number of iterations.
        steady_state (bool):
            Toggle whether solving steady state (dT/dt = 0) or time dependent
            problem.
    """

    # Variables that must be present for the mixin.
    # These will be replaced by the init in te class this is mixed into.
    V = None
    T = None
    v = None
    a = None
    L = None

    def __init__(self, *args, **kwargs):
        """
        Initialiser for TimeMixin.

        Add M/dt to a and L.
        """
        super().__init__(*args, **kwargs)

        self.T_ = Function(self.V, name='T_')
        self._delT = Function(self.V, name='delT')

        self.C = Function(self.V, name='C')

        self.t_max = 1e-9
        self.dt = 1e-10
        self._dt_invc = Constant(0)
        self.steps = self.t_max/self.dt

        self.steady_state = True

        self.a += self._M()

    def approx_delT(self, F=None):
        """
        Replace the delT placeholder with the simple finite difference
        approximation:
        dT/dt ~ (T - T_)/delta_t

        Args:
            F (Function, optional):
                The function to replace `delT` in. If None, this will use
                `self.a`. Defaults to None.

        Returns:
            Function: The updated F.
        """
        delT = (self.T - self.T_)*self._dt_invc
        return replace(F, {self._delT: delT})

    def remove_timescale(self):
        """
        Set 1/dt to 0 so that the M terms vanish.
        """
        self.steady_state = True
        self._dt_invc.assign(0)

    def set_timescale(self, t_max=None, dt=None, steps=None):
        """
        Set the time stepping variables (t_max, dt, and number of steps).
        This method is designed to be given 2 variables and calculate the
        third. If 3 variables are given it will check that they are consistent.

        Args:
            t_max (float, optional):
                The time to iterate until. Defaults to None.
            dt (float, optional):
                The increase in time for each iteration. Defaults to None.
            steps (int, optional):
                The number of steps to take. Defaults to None.

        Raises:
            ValueError: If less than 2 variables are provided.
            ValueError: If 3 values are provided which are inconsistent.
            RuntimeWarning: If steps is not an int.
        """
        num_var_none = 0
        if t_max is None:
            num_var_none += 1
        if dt is None:
            num_var_none += 1
        if steps is None:
            num_var_none += 1
        if num_var_none > 1:
            raise ValueError('Must specify at least 2 of total, dt, and steps')

        if num_var_none == 0 and t_max != dt*steps:
            raise ValueError('Conflicting arguments. Try specifying only 2 of '
                             'total, dt, and steps.')

        if t_max is None:
            t_max = dt*steps
        if dt is None:
            dt = t_max/steps
        if steps is None:
            steps = t_max/dt

        if steps != int(steps):
            steps = int(steps + 1)
            raise RuntimeWarning("steps is not an integer, rounding up.")

        self.t_max = t_max
        self.dt = dt
        self._dt_invc.assign(1/dt)
        self.steps = steps
        self.steady_state = False

    def set_C(self, C):
        """
        Update C in all formulas (namely a).

        Args:
            C (Function):
                The heat capacity for the problem.
        """
        self.a = replace(self.a, {self.C: C})
        self.C = C

    def _M(self):
        """
        Create the mass matrix section.

        Returns:
            Function: The complete mass matrix section using delT.
        """
        return self.C*self._delT*self.v*dx
