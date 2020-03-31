"""
Implements a class to act as a dispatch table for methods.
"""

from firedrake import replace


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

    def update(self, F, method='BackwardEuler', **kwargs):
        """
        Update the given F using the correct method.

        Args:
            F (Function):
                The function to update.
            method (str, optional):
                The method to use. Defaults to 'BackwardEuler'.

        Raises:
            ValueError: If the method does not exist.

        Returns:
            Function: The updated function.
        """
        if method[0] == '_':
            raise ValueError('Not a valid method.')
        try:
            return getattr(self, method)(F, **kwargs)
        except KeyError:
            raise ValueError('Not a valid method.')

    def BackwardEuler(self, F):
        """
        Backward Euler leaves T as T in the setup that is used.

        Args:
            F (Function): The function to update.

        Returns:
            Function: The updated function
        """
        # pylint: disable=no-self-use
        return F

    def ForwardEuler(self, F):
        """
        Forward Euler sets T to T_ in the setup that is used.

        Args:
            F (Function): The function to update.

        Returns:
            Function: THe updated function
        """
        return replace(F, {self.T, self.T_})

    def CrankNicolson(self, F):
        """
        Crank Nicolson sets T to (T + T_)/2 in the setup that is used.

        Args:
            F (Function): The function to update.

        Returns:
            Function: THe updated function
        """
        T = 0.5*(self.T + self.T_)
        return replace(F, {self.T, T})

    def Theta(self, F, theta):
        """
        The Theta model sets T to a weighted mean of T and T_.
        This takes 1 extra argument which is the weighting.

        Setting:
          theta=0.0 is equivalent to ForwardEuler
          theta=0.5 is equivalent to CrankNicholson
          theta=1.0 is equivalent to BackwardEuler

        Args:
            F (Function): The function to update.
            theta (float):
                Weight of T (the weight of T_ is 1-theta)
        """
        T = theta*self.T + (1-theta)*self.T_
        return replace(F, {self.T: T})
