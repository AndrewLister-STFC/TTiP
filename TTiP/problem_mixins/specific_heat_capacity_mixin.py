"""
Contains the heat capacity classes for extending problems.
"""
from scipy.constants import e


class ConstantIonisationSHCMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow a specific heat capacity
    for constant ionisation problems.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(ConstantIonisationSHCMixin, Problem):
           pass

    Attributes:
        electron_density (Function):
            The density of electrons in the plasma.
        C (Function):
            The specific heat capacity.
    """
    # pylint: disable=no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for ConstantIonisationSHCMixin.

        Replaces C (Specific heat capacity) with the formula for assumed
        constant ionisation.
        """
        super().__init__(*args, **kwargs)

        self._add_function('electron_density')
        self._add_function('C')

        C = 1.5 * self.electron_density * e
        self.set_function('C', C)


class NonConstantIonisationSHCMixin:
    """
    Class to extend Problems as a mixin.
    This mixin extends the problem to allow a specific heat capacity
    for non-constant ionisation problems.
    To use, define a new class with this in the inheritance chain.
    i.e::
       class NewProblem(NonConstantIonisationSHCMixin, Problem):
           pass

    Attributes:
        ionisation (Function):
            The ionisation energy for the plasma.
        ion_density (Function):
            The density of ions in the plasma.
        C (Function):
            The specific heat capacity.
    """
    # pylint: disable=no-member

    def __init__(self, *args, **kwargs):
        """
        Initialiser for ConstantIonisationSHCMixin.

        Replaces C (Specific heat capacity) with the formula for
        non-constant ionisation.
        """
        super().__init__(*args, **kwargs)

        self._add_function('ionisation')
        self._add_function('ion_density')
        self._add_function('C')

        C = 1.5 * self.ionisation * self.ion_density * e
        self.set_function('C', C)
