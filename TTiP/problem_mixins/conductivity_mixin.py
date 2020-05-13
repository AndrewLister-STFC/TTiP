"""
Contains the conductivity classes for extending problems.
"""
from firedrake import Function, sqrt
from scipy.constants import e, epsilon_0, m_e, pi


class SpitzerHarmMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow spitzer harm conductivity.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(SpitzerHarmMixin, Problem):
           pass

    Required Attributes (for mixin):
        V (FunctionSpace):
            The function space that functions must be defined on.
        T (Function):
            The trial function to solve for.
        K (Function):
            The conductivity (will be updated by this mixin)

    Attributes:
        coulomb_ln (Function):
            The coulomb logarithm for the problem.
        Z (Function):
            The ionisation term for the problem.
    """
    # pylint: disable=too-few-public-methods

    # Variables that must be present for the mixin.
    # These will be replaced by the init in te class this is mixed into.
    T = None

    def __init__(self, *args, **kwargs):
        """
        Initialiser for SpitzerHarmMixin.

        Creates a new conductivity term and replaces K in all functions.
        """
        super().__init__(*args, **kwargs)

        self.coulomb_ln = Function(self.V)
        self.Z = Function(self.V)
        K = self._K()
        self._update_func('K', K)

        K_min = self.K_min()
        self.bound('K', lower=K_min)

    def _K(self):
        """
        Create the function that defines the conductivity.

        Returns:
            Function: The Spitzer-Harm conductivity
        """
        tmp = 288 * pi * sqrt(2) * epsilon_0**2 / sqrt(e * m_e)
        tmp = tmp * pow(self.T, 5 / 2) / (self.coulomb_ln * self.Z)

        return tmp

    def _K_min(self):
        r = (3 / (4 * pi * self.density))**(1 / 3)
        tau = r / self.v_th
        tmp = 48 * self.Z * self.density * e**2 * self.T * tau / sqrt(pi) / m_e

        return tmp

    def set_coulomb_ln(self, coulomb_ln):
        """
        Set the coulomb logarithm in K (and propagate).

        Args:
            coulomb_ln (Function): The function to replace coulomn_ln with.
        """
        self._update_func('coulomb_ln', coulomb_ln)

    def set_Z(self, Z):
        """
        Set the ionization energy in K (and propagate).

        Args:
            Z (Function): The function to replace Z with.
        """
        self._update_func('Z', Z)
