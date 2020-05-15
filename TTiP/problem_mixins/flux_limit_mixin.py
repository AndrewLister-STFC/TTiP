"""
Contains the FluxLimiterMixin class for extending problems.
"""
from scipy.constants import e


class FluxLimiterMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow flux limiting.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(FluxLimiter, Problem):
           pass

    Required Attributes (for mixin):
        T (Funtion):
            The temperature of the plasma.
        electron_density (Function):
            The electron density of the plasma.
        v_th (Function):
            Another parameter (thermal velocity?)
        q (Function):
            The flux term for the plasma.
    """
    # pylint: disable=no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for FluxLimiterMixin.

        Replace the flux with a bounded version.
        """
        super().__init__(*args, **kwargs)

        self._add_function('T')
        self._add_function('electron_density')
        self._add_function('v_th')
        self._add_function('q')

        q_fs = self._q_fs()
        self.bound('q', lower=-0.3 * q_fs, upper=0.3 * q_fs)

    def _q_fs(self):
        """
        Create the flux limit.

        returns:
            Function: The flux limit.
        """
        return self.electron_density * e * self.T * self.v_th
