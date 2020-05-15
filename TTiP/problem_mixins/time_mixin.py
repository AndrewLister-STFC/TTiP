"""
Contains the TimeMixin class for extending problems.
Also contains the IterationMethod class used by TimeMixin.
"""
from firedrake import Constant, Function, dx
from scipy.constants import e

from TTiP.util.logger import get_logger

LOGGER = get_logger()


class TimeMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow time stepping by adding the dT/dt
    term.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(TimeMixin, Problem):
           pass

    Attributes:
        T (firedrake.Function):
            The trial function for the problem.
        v (firedrake.Function):
            The test function for the problem.
        a (firedrake.Function):
            The section containing the combination of terms involving both T
            and v.
        electron_density (firedrake.Function):
            The electron density of the plasma.
        T_ (firedrake.Function):
            A function used to hold the previous value for T.
        C (firedrake.Function):
            A function used to hold the heat capacity of the mesh.
        _delT (firedrake.Function):
            A function used as a placeholder for the time derivative.
        max_t (float):
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
    # pylint: disable=too-many-instance-attributes, no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for TimeMixin.

        Add M/dt to a and L.
        """
        super().__init__(*args, **kwargs)

        self._add_function('T')
        self._add_function('a')
        self._add_function('electron_density')

        self._add_function('T_')
        self._add_function('C')
        self._add_function('_delT')

        self.max_t = 1e-9
        self.dt = 1e-10
        self._dt_invc = Constant(0)
        self.steps = self.max_t / self.dt

        self.steady_state = True

        self.C = self._C()
        self.a += self._M()

    def set_method(self, method='BackwardEuler', **kwargs):
        """
        Replace T with the correct substitution for the method, then replace
        the delT placeholder with the simple finite difference approximation:
        dT/dt ~ (T - T_)/delta_t

        Args:
            method (str, optional):
                The method to use. Defaults to 'BackwardEuler'.
        """
        T = self.T
        iter_method = IterationMethod(self)
        substitution = iter_method.get_substitution(method, **kwargs)
        self._update_func('T', substitution)
        self.T = T

        delT = (self.T - self.T_) * self._dt_invc
        self._update_func('_delT', delT)

    def remove_timescale(self):
        """
        Set 1/dt to 0 so that the M terms vanish.
        """
        self.steady_state = True
        self._dt_invc.assign(0)

    def set_timescale(self, max_t=None, dt=None, steps=None):
        """
        Set the time stepping variables (max_t, dt, and number of steps).
        This method is designed to be given 2 variables and calculate the
        third. If 3 variables are given it will check that they are consistent.

        Args:
            max_t (float, optional):
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
        if max_t is None:
            num_var_none += 1
        if dt is None:
            num_var_none += 1
        if steps is None:
            num_var_none += 1
        if num_var_none > 1:
            raise ValueError('Must specify at least 2 of max_t, dt, and steps')

        if num_var_none == 0:
            calc_steps = int(max_t / dt)
            if calc_steps != max_t / dt:
                calc_steps += 1

            if steps != calc_steps:
                raise ValueError('Conflicting arguments. Try specifying only 2'
                                 ' of max_t, dt, and steps.')

        if max_t is None:
            max_t = dt * steps
        if dt is None:
            dt = max_t / steps
        if steps is None:
            steps = max_t / dt

        if steps != int(steps):
            steps = int(steps + 1)
            LOGGER.warning("steps is not an integer, rounding up.")

        self.max_t = max_t
        self.dt = dt
        self._dt_invc.assign(1 / dt)
        self.steps = steps
        self.steady_state = False

    def _M(self):
        """
        Create the mass matrix section.

        Returns:
            Function: The complete mass matrix section using delT.
        """
        return self.C * self._delT * self.v * dx

    def _C(self):
        """
        Create the specific heat capacity.

        Returns:
            Function: The specific heat capacity.
        """
        return 1.5 * self.electron_density * e


class IterationMethod:
    """
    Dispatch table style class.
    """

    def __init__(self, problem):
        """
        Initializer for the IterationMethod.
        Defines new and old T.

        Args:
            problem (TimeMixin, Problem):
                The problem to take T and T_ from.
        """
        self.T = problem.T
        self.T_ = problem.T_

    def get_substitution(self, method, **kwargs):
        """
        Return the function to substitute in place of T for the given method.

        Args:
            method (str):
                The method to use.

        Raises:
            ValueError: If the method does not exist.

        Returns:
            Function: The function to substitute T for.
        """
        if method[0] == '_':
            raise ValueError('Not a valid method.')
        try:
            return getattr(self, method)(**kwargs)
        except AttributeError:
            raise ValueError('Not a valid method.')

    def BackwardEuler(self):
        """
        Backward Euler leaves T as T in the setup that is used.

        Returns:
            Function: The function to substitute T for.
        """
        return self.T

    def ForwardEuler(self):
        """
        Forward Euler sets T to T_ in the setup that is used.

        Returns:
            Function: The function to substitute T for.
        """
        return self.T_

    def CrankNicolson(self):
        """
        Crank Nicolson sets T to (T + T_)/2 in the setup that is used.

        Returns:
            Function: THe updated function
        """
        return 0.5 * (self.T + self.T_)

    def Theta(self, theta):
        """
        The Theta model sets T to a weighted mean of T and T_.
        This takes 1 extra argument which is the weighting.

        Setting:
          theta=0.0 is equivalent to ForwardEuler
          theta=0.5 is equivalent to CrankNicholson
          theta=1.0 is equivalent to BackwardEuler

        Args:
            theta (float):
                Weight of T (the weight of T_ is 1-theta)

        Returns:
            Function: The function to substitute T for.
        """
        return theta * self.T + (1 - theta) * self.T_
