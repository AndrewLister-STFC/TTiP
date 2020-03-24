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

    def update(self, F, method='BackwardEuler'):
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
            return self.__dict__[method](F)
        except KeyError:
            raise ValueError('Not a valid method.')

    def BackwardEuler(self, F):
        """
        Backward Euler leaves T as T in the setup that is used.

        Args:
            F (Function): The function to update.

        Returns:
            Function: THe updated function
        """
        return F

    def ForwardEuler(self, F):
        """
        Forward Euler sets T to T_ in the setup that is used.

        Args:
            F (Function): The function to update.

        Returns:
            Function: THe updated function
        """
        F = replace(F, {self.T, self.T_})
        return F
