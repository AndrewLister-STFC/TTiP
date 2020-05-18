"""
Contains the conductivity classes for extending problems.
"""
from firedrake import sqrt
from scipy.constants import e, epsilon_0, m_e, pi


class SpitzerHarmMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow spitzer harm conductivity.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(SpitzerHarmMixin, Problem):
           pass

    Attributes:
        T (Function):
            The trial function to solve for.
        K (Function):
            The conductivity (will be updated by this mixin)
        coulomb_ln (Function):
            The coulomb logarithm for the problem.
        z (Function):
            The ionisation term for the problem.
    """
    # pylint: disable=too-few-public-methods, no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for SpitzerHarmMixin.

        Creates a new conductivity term and replaces K in all functions.
        """
        super().__init__(*args, **kwargs)

        self._add_function('T')
        self._add_function('K')
        self._add_function('coulomb_ln')
        self._add_function('z')

        self.set_function('K', self._K())

    def _K(self):
        """
        Create the function that defines the conductivity.

        Returns:
            Function: The Spitzer-Harm conductivity
        """
        tmp = 288 * pi * sqrt(2) * epsilon_0**2 / sqrt(e * m_e)
        tmp = tmp * pow(self.T, 5 / 2) / (self.coulomb_ln * self.z)

        return tmp


class ConductivityLimiterMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to place a lower limit on the conductivity.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(ConductivityLimiterMixin, Problem):
           pass

    Attributes:
        T (Function):
            The electron temperature in the plasma.
        ion_density (Function):
            The density of ions in the plasma.
        z (Function):
            The ionization term.
        v_th (Function):
            The value of v_th (thermal velocity?)
        K (Function):
            The conductivity of the plasma.
    """
    # pylint: disable=too-few-public-methods, no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for ConductivityLimiterMixin.

        Inserts a lower bound on the conductivity.
        """
        super().__init__(*args, **kwargs)

        self._add_function('T')
        self._add_function('ion_density')
        self._add_function('z')
        self._add_function('v_th')
        self._add_function('K')

        K_min = self._K_min()
        self.bound('K', lower=K_min)

    def _K_min(self):
        r_ii = (3 / (4 * pi * self.ion_density))**(1 / 3)
        tau_min = r_ii / self.v_th
        tmp = 48 * self.z * self.ion_density * e**2 * self.T * tau_min
        tmp = tmp / sqrt(pi) / m_e

        return tmp
