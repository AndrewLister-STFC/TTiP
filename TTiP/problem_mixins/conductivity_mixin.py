"""
Contains the conductivity classes for extending problems.
"""
from scipy.constants import e, epsilon_0, m_e, pi

from firedrake import Constant, replace, sqrt


class SpitzerHarmMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow spitzer harm conductivity.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(SpitzerHarmMixin, Problem):
           pass

    Required Attributes (for mixin):
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

        Creates a new conductivity term and replaces it in a and L.
        """
        super().__init__(*args, **kwargs)

        self.coulomb_ln = self._coulomb_ln()
        self.Z = self._Z()
        K = self._K()
        self.set_K(K)

    def set_K(self, K):
        """
        Set the value for K in self.a and self.L.

        Args:
            K (Function): The function so replace K with.
        """
        self.a = replace(self.a, {self.K: K})
        self.L = replace(self.L, {self.K: K})
        self.K = K

    def _K(self):
        """
        Create the function that defines the conductivity.

        Returns:
            Function: The Spitzer-Harm conductivity
        """
        tmp = 288 * pi * sqrt(2) * epsilon_0**2 / sqrt(e * m_e)
        tmp = tmp * pow(self.T, 5 / 2) / (self.coulomb_ln * self.Z)

        return tmp

    def _coulomb_ln(self):
        """
        Create the coulomb logarithm.

        Returns:
            Function: The coulomb log.
        """
        # pylint: disable=no-self-use
        return Constant(10)

    def _Z(self):
        """
        Create the ionization energy.

        Returns:
            Function: The ionization energy.
        """
        # pylint: disable=no-self-use
        return Constant(12)
