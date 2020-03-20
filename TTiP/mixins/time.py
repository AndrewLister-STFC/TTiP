"""
Contains the TimeMixin class for extending problems.
"""
from firedrake import Constant, Function, dx


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
        C (firedrake.Function):
            A function used to hold the heat capacity of the mesh.
        t_max (float):
            The time to iterate up to.
        dt (float):
            The size of each time step. 
        dt_invc (firedrake.Constant):
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

    def __init__(self):
        """
        Initialiser for TimeMixin.

        Add M/dt to a and L.
        """
        super().__init__()

        self.T_ = Function(self.V)
        self.C = Function(self.V)

        self.t_max = 1e-9
        self.dt = 1e-10
        self.dt_invc = Constant(0)
        self.steps = self.t_max/self.dt

        M = self._M(self.T)
        M_ = self._M(self.T_)
        self.steady_state = True

        self.a += M*self.dt_invc
        self.L += M_*self.dt_invc

    def remove_timescale(self):
        """
        Set 1/dt to 0 so that the M terms vanish.
        """
        self.steady_state = True
        self.dt_invc.assign(0)

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
        self.dt_invc.assign(1/dt)
        self.steps = steps
        self.steady_state = False

    def _M(self, T=None):
        """
        Create the mass matrix section.

        Args:
            T (Function, optional):
                The function to put in the mass matrix. This is useful for
                changing time step methods. Defaults to None.

        Returns:
            Function: The complete mass matrix section in the var passed.
        """
        if T is None:
            T = self.T

        return self.C*T*self.dt_invc*self.v*dx
