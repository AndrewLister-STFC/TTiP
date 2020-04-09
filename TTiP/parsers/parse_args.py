"""
Utility module for parsing args.
"""

import operator
from abc import ABC, abstractmethod


class Node(ABC):
    """
    Abstract base class for a node in the equation parsing.

    For any node, call evaluate to get the parsed value including all children.

    Attributes:
        _parent (Node): The node that this one branches from.
    """

    def __init__(self):
        """
        Initialise the parent ot None.
        """
        self._parent = None

    @abstractmethod
    def evaluate(self):
        """
        This should return a value for the node.
        """
        raise NotImplementedError


class Expression(Node):
    """
    An Expression node.
    This object will parse an expression into a tree.

    Usage:
        Initialise this class with a string.
        Call evaluate to get the parsed result.

    Attributes:
        operators (dict):
            A mapping from string representations of operators to tuples of
            priority and callable.
        _left (Node):
            The Node to evaluate as the left arg of the operator.
        _right (Node):
            The Node to evaluate as the right arg of the operator.
        _parent (Node):
            The Node that this Node is an arg to.
        _op (tuple<int, callable>):
            A pair of priority and operator callable for the Expression.
            If priority is higher it will be evaluated before other operators.
    """
    operators = {'+': (0, operator.add),
                 '-': (0, operator.sub),
                 '/': (1, operator.truediv),
                 '*': (1, operator.mul),
                 '^': (2, operator.pow),
                 '<terminal>': (3, lambda l, r: l)}

    def __init__(self, s):
        """
        Initialiser for the Expression class.

        Args:
            s (str): The string to parsse into an equation.
        """
        self._parent = None
        self._left = None
        self._right = None
        self._op = None

        # If first char is an open bracket, eval everything up to the last
        # closing bracket as the left arg.
        if s[0] == '(':
            left, rem = s[1:].split(')', 1)
            while left.count('(') != left.count(')') - 1:
                if not rem:
                    raise ValueError('Unclosed brackets detected in: {}'
                                     ''.format(s))
                tmp, rem = rem.split(')', 1)
                left = left + ')' + tmp

            self._set_left(Expression(left))

            if rem:
                self._op = self.operators[rem[0]]
                self._set_right(Expression(rem[1:]))
            else:
                self._op = self.operators['<terminal>']
                self._right = None

            return

        # For each operator split the string and take the split that minimises
        # the left argument as this will be first.
        best_partition = [s, '', '']
        for o in self.operators:
            part = s.partition(o)
            if len(part[0]) < len(best_partition[0]):
                best_partition = part

        # Check that an operator was found.
        if best_partition[0] == s:
            # No operator so set left to be a terminal
            self.op = self.operators['<terminal>']
            self._set_left(Terminal(s))
            self._right = None
        else:
            self._op = self.operators[best_partition[1]]
            self._set_left(Expression(best_partition[0]))
            self._set_right(Expression(best_partition[2]))

    def _set_left(self, f):
        """
        Update the left argument for the function.

        Args:
            f (func or terminal): The fucntion that will be the left arg.
        """
        self._left = f

    def _set_right(self, f):
        r"""
        Update the right argument of the function.
        If the operator of the function has a lower or equal priority propagate
        up one level.
        The propagate step is as follows:

        parent        f         parent
            \        / \            \
            self    x   y   ->       f
            /                       / \
           l                    self   y
                                /  \
                               l    x

        Args:
            f (func or terminal): The function to set as the right arg.
        """
        if self._op[0] > f._op[0]:
            self._right = f
            f._parent = self
        else:
            self._set_right(f._left)
            f._set_left(self)
            if self._parent is not None:
                self._parent._set_right(f)
            self._parent = f

    def evaluate(self):
        """
        Evaluate the tree and return the correctly parsed equation.

        Returns:
            float, int, firedrake equation:
                The parsed function for use with firedrake.
        """
        if isinstance(self._left, Node):
            self._left = self._left.evaluate()
        if isinstance(self._right, Node):
            self._right = self._right.evaluate()
        return self.operators[self._op](self._left, self._right)


class Terminal(Node):
    """
    A terminal node for expressions.
    This is used to process values or variables.

    Convert a string into the correct value.
    e.g. "2" -> 2 (int)
        "false" -> False (bool)
        "1.8" -> 1.8 (float)
        "1.2, false" -> [1.2, False] (list)
    """

    def __init__(self, s):
        """
        Initialiser for the Terminal class.

        Args:
            s (str): The string to parse as a terminal.
        """
        self._string = s

    def evaluate(self):
        """
        Evaluate the terminal and return the parsed value

        Returns:
            (varies): The parsed terminal.
        """
        if self._string.lower() == 'true':
            return True
        if self._string.lower() == 'false':
            return False

        try:
            val = int(self._string)
            return val
        except ValueError:
            pass

        try:
            val = float(self._string)
            return val
        except ValueError:
            pass

        return self._string.strip('"').strip("'")


def process_arg(val):
    """
    Convert a string into the correct value.
    e.g. "2" -> 2 (int)
         "false" -> False (bool)
         "1.8" -> 1.8 (float)
         "1.2, false" -> [1.2, False] (list)

    Args:
        val (string): The value to convert.

    Returns:
        (Various): The converted value.
    """
    val = val.replace(' ', '')
    if ',' in val:
        return [process_arg(v) for v in val.split(',')]

    expression = Expression(val)
    return expression.evaluate()
