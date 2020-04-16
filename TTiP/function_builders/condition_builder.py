r"""
The condition function allows the user to create a stepped function using an
operator alongside a left and right hand side (lhs and rhs respectively).

The exact formula is:

.. math::

    \text{Condition}(x, \text{operator}, \text{lhs}, \text{rhs}) =
    \begin{cases}
    1, &\text{lhs} \text{ operator } \text{rhs}\\
    0, &\text{otherwise}
    \end{cases}

Where:

- operator is an operator ('<', '>', '<=', '==', ...)
- lhs is an expression for the left hand side
- rhs is an expression for the right hand side

e.g.

.. math::

    \text{Condition}(\vec{x}, <, x^2 + y^2, 10) =
    \begin{cases}
    1, & x_1^2 + x_2^2 < 10\\
    0, &\text{otherwise}
    \end{cases}

"""
from firedrake import Function, conditional, eq, ge, gt, le, lt, ne
from TTiP.function_builders.function_builder import FunctionBuilder
from ufl.core.expr import Expr


class ConditionBuilder(FunctionBuilder):
    """
    A FunctionBuilder to create a conditionally valued function.

    Required Properties:
        operator (str):
            This is the value that the constant will have.
        lhs (str, int, float, ufl.Expr):
            This will be the left hand side of the operator.
        rhs (str, int, float, ufl.Expr):
            This will be the right hand side of the operator.
    """

    properties = {'operator': (str),
                  'lhs': (str, int, float, Expr),
                  'rhs': (str, int, float, Expr)}

    _dispatch_table = {'<': lt,
                       '<=': le,
                       '>': gt,
                       '>=': ge,
                       '=': eq,
                       '==': eq,
                       '!=': ne,
                       '~=': ne,
                       'lt': lt,
                       'le': le,
                       'gt': gt,
                       'ge': ge,
                       'eq': eq,
                       'ne': ne}

    def build(self):
        """
        Build the conditionally valued firedrake function.

        Raises:
            AttributeError: If required properties are not defined.
            AttributeError: If operator not in allows list.

        Returns:
            Function:
                firedrake function set to 1 where the condition is met and 0
                where it is not.
        """
        for k in self.properties:
            if self._props[k] is None:
                raise AttributeError('"{}" has not been defined.'.format(k))

        op = self._props['operator']
        lhs = self._props['lhs']
        rhs = self._props['rhs']

        if op not in self._dispatch_table:
            raise AttributeError('Unknown condition: {}'.format(op))

        val = conditional(self._dispatch_table[op](lhs, rhs), 1, 0)
        return Function(self.V).interpolate(val)
