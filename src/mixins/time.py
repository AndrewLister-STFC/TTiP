from firedrake import Constant, dx


class TimeMixin:

    # Variables that must be present for the mixin.
    V = None
    T = None
    T_ = None
    v = None
    a = None
    L = None

    def __init__(self):
        super().__init__()

        self.C = Function(self.V)

        self.t_max = 1e-9
        self.dt = 1e-10
        self.dt_invc = Constant(0)
        self.steps = self.t_max/self.dt

        self.M = self._M(self.T)
        self.M_ = self._M(self.T_)
        self._steady_state = True

        self.a += self.M*self.dt_invc
        self.L += self.M_*self.dt_invc

    def remove_timescale(self):
        self._steady_state = True
        self.dt_invc.assign(0)

    def set_timescale(self, total=None, dt=None, steps=None):
        num_var_none = 0
        if total is None:
            num_var_none += 1
        if dt is None:
            num_var_none += 1
        if steps is None:
            num_var_none += 1
        if num_var_none > 1:
            raise ValueError('Must specify at least 2 of total, dt, and steps')

        if num_var_none == 0 and total != dt*steps:
            raise ValueError('Conflicting arguments. Try specifying only 2 of '
                             'total, dt, and steps.')

        if total is None:
            total = dt*steps
        if dt is None:
            dt = total/steps
        if steps is None:
            steps = total/dt

        if steps != int(steps):
            steps = int(steps + 1)
            raise RuntimeWarning("steps is not an integer, rounding up.")

        self.t_max = total
        self.dt = dt
        self.dt_invc.assign(1/dt)
        self.steps = steps
        self.steady_state = False

    def _M(self, T=None):
        if T is None:
            T = self.T

        return self.C*T*self.dt_invc*self.v*dx
