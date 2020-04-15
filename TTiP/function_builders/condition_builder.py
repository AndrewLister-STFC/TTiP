r"""
The condition function allows the user to create a stepped function using a 

"""
from firedrake import Function, conditional, eq, ge, gt, le, lt, ne
from TTiP.function_builders.function_builder import FunctionBuilder
from ufl.core.expr import Expr

class ConditionBuilder(FunctionBuilder):

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
        op = self._props['operator']
        lhs = self._props['lhs']
        rhs = self._props['rhs']

        if op not in self._dispatch_table:
            raise AttributeError('Unknown condition: {}'.format(op))

        val = conditional(self._dispatch_table[op](lhs, rhs), 1, 0)
        return Function(self.V).interpolate(val)
