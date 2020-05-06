"""
Utility module for parsing args.
"""

import operator
from abc import ABC, abstractmethod

from firedrake import Function, SpatialCoordinate, cos, exp, sin, tan, sqrt
# pylint: disable=attribute-defined-outside-init,arguments-differ
# pylint: disable=protected-access


class Node(ABC):
    """
    Abstract base class for a node in the equation parsing.

    For any node, call evaluate to get the parsed value including all children.

    Class Attributes:
        _reserved_terminals (list<string>):
            A list of strings that are reserved.
            e.g. "false"
        _custom_terminals (dict):
            A dictionary holding a global (across all nodes) list of custom
            terminals. Custom terminals will be a name and corresponding result
            for the evaluation.

    Attributes:
        _parent (Node): The node that this one branches from.
        used_terminals (list<str>):
            Which terminals have been used in the node and children.
    """

    _reserved_terminals = []
    _custom_terminals = {}

    def __new__(cls, *args, **kwargs):
        """
        Override new to ensure that the root node is returned from building the
        tree.

        Returns:
            Node: The root node of the generated tree.
        """
        instance = super().__new__(cls)
        instance._init(*args, *kwargs)
        return instance.root()

    def __init__(self, *args, **kwargs):
        """
        Initialiser for Node.
        Note: This is not used.
              Initialising is performed by _init below to prevent __new__ from
              reinitialising objects.
        """
        # pylint: disable=unused-argument
        return

    def _init(self):
        """
        Initialise the parent to None.

        Args:
            s (str): The string to parsse into an equation.
        """
        super().__init__()
        self._parent = None
        self._used_terminals = []

    @property
    def used_terminals(self):
        """
        Getter for _used_terminals

        Returns:
            list<str>:
                The names of terminals that have been used in this node or it's
                children.
        """
        return self._used_terminals

    def ready(self):
        """
        Check that all used terminals have been defined.
        """
        for t in self.used_terminals:
            if self._custom_terminals[t] is None:
                return False

        return True

    @abstractmethod
    def evaluate(self, mesh=None, V=None):
        """
        This should return a value for the node.

        Args:
            mesh (Mesh, optional):
                The firedrake mesh to evaluate the value for.
                Defaults to None.
            V (FunctionSpace, optional):
                The firedrake functionspace that spatial coords will be
                evaluated over. Defaults to None.
        """
        raise NotImplementedError

    def root(self):
        """
        Return the top level of the expression tree.

        Returns:
            None: The top level node (root of the tree).
        """
        if self._parent is None:
            return self
        return self._parent.root()

    @classmethod
    def clear_terminals(cls):
        """
        Clear the custom terminals. It is advised that this is done before
        parsing any new sections.
        """
        cls._custom_terminals.clear()

    @classmethod
    def subscribe_terminal(cls, name, value=None):
        """
        Add a terminal to the list of custom terminals.

        Args:
            name (str): The name to subscibe
            value (Any, optional):
                The value of the terminal if available. Defaults to None.
        """
        if name in cls._custom_terminals:
            raise AttributeError('{} already subscribed. To update use '
                                 '"update_terminal"'.format(name))
        cls._custom_terminals[name] = value

    @classmethod
    def update_terminal(cls, name, value):
        """
        Add a terminal to the list of custom terminals.

        Args:
            name (str): The name to subscibe
            value (Any, optional):
                The value of the terminal if available. Defaults to None.
        """
        if name not in cls._custom_terminals:
            raise AttributeError('{} not subscribed. To subscribe use '
                                 '"subscribe_terminal"'.format(name))
        cls._custom_terminals[name] = value


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
    operators = {'+': (0, operator.add, '+'),
                 '-': (0, operator.sub, '-'),
                 '/': (1, operator.truediv, '/'),
                 '*': (1, operator.mul, '*'),
                 '^': (2, operator.pow, '^'),
                 'e': (3, lambda x, y: x * 10**y, 'e'),
                 '<negate>': (4, lambda l, r: -r, '-'),
                 '<left>': (11, lambda l, r: l, '')}

    function_priority = 10
    functions = {'abs': abs,
                 'cos': cos,
                 'exp': exp,
                 'sin': sin,
                 'sqrt': sqrt,
                 'tan': tan
                 }

    def _init(self, s):
        """
        Initialiser for the Expression class.

        Args:
            s (str): The string to parsse into an equation.
        """
        super()._init()
        self._parent = None
        self._left = None
        self._right = None
        self._op = None
        s = s.strip()

        # Check if list (comma seperated).
        if ',' in s:
            self.set_left(List(s))
            self._op = self.operators['<left>']
            return

        # If first char is an open bracket, eval everything up to the last
        # closing bracket as the left arg.
        if s[0] == '(':
            left, rem = s[1:].split(')', 1)
            while left.count('(') != left.count(')'):
                if not rem:
                    raise ValueError('Unclosed brackets detected in: {}'
                                     ''.format(s))
                tmp, rem = rem.split(')', 1)
                left = left + ')' + tmp

            if rem:
                self.set_left(Expression('(' + left + ')'))
                self._op = self.operators[rem[0]]
                self.set_right(Expression(rem[1:]))
            else:
                self.set_left(Expression(left))
                self._op = self.operators['<left>']
                self._right = None
            return

        # Check for negate
        if s[0] == '-':
            self._left = None
            self._op = self.operators['<negate>']
            self.set_right(Expression(s[1:]))
            return

        # Check if s starts with a function.
        for func_name, func in self.functions.items():
            if s.startswith(func_name + '('):
                self._left = None
                self._op = (self.function_priority, func, func_name)
                self.set_right(Expression(s[len(func_name):]))
                return

        # Check if s starts with a custom or reserved terminal.
        for t in list(self._custom_terminals) + self._reserved_terminals:
            if s.startswith(t):
                tmp_s = s[len(t):].strip()
                if tmp_s.startswith(tuple(self.operators.keys())) or not tmp_s:
                    self.set_left(Terminal(t))
                    s = tmp_s
                    if not s:
                        self._op = self.operators['<left>']
                        self._right = None
                        return
                    break

        # For each operator split the string and take the split that minimises
        # the left argument as this will be first.
        best_partition = (s, '', '')
        for o in self.operators:
            part = s.partition(o)
            is_left = self._left is not None or part[0]
            if is_left and len(part[0]) < len(best_partition[0]):
                best_partition = part

        left, op, right = best_partition

        # Check that an operator was found.
        if left == s:
            # No operator so set left to be a terminal with s.
            self._op = self.operators['<left>']
            if self._left is None:
                self.set_left(Terminal(s))
            else:
                raise RuntimeError('Failed to parse input: {}'.format(s))
            self._right = None
        else:
            self._op = self.operators[op]
            if self._left is None:
                self.set_left(Terminal(left))
            self.set_right(Expression(right))

    def set_left(self, f):
        """
        Update the left argument for the function.

        Args:
            f (Node): The node that will be the left arg.
        """
        self._left = f
        f._parent = self

    def set_right(self, f):
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
            f (Node): The function to set as the right arg.
        """
        if isinstance(f, Terminal):
            self._right = f
            f._parent = self
        else:
            if self._op[0] < f._op[0]:
                self._right = f
                f._parent = self
            else:
                # Cut left arg off f.
                left = f._left
                f._left = None
                left._parent = None
                # Cut self off parent
                parent = self._parent
                self._parent = None
                # Set right arg to what was f._left
                self.set_right(left)
                # Set f._left to self
                f.set_left(self.root())
                if parent is not None:
                    # At this point, parent can only be Expression so disable
                    # pylint warning.
                    # pylint: disable=no-member
                    parent.set_right(f)

    def evaluate(self, mesh=None, V=None):
        """
        Evaluate the tree and return the correctly parsed equation.

        Args:
            mesh (Mesh, optional):
                The firedrake mesh to evaluate the value for.
                Defaults to None.
            V (FunctionSpace, optional):
                The firedrake functionspace that spatial coords will be
                evaluated over. Defaults to None.

        Returns:
            float, int, firedrake equation:
                The parsed function for use with firedrake.
        """
        left = self._left
        right = self._right
        if isinstance(left, Node):
            left = left.evaluate(mesh, V)
        if isinstance(right, Node):
            right = right.evaluate(mesh, V)
        try:
            if self._op[2] in self.functions:
                return self._op[1](right)
            return self._op[1](left, right)
        except TypeError:
            raise RuntimeError('Failed to evaluate "{}".'.format(str(self)))

    @property
    def used_terminals(self):
        """
        Property to dynamically return used terminals.
        Used terminals are a sum of the used terminals of it's children.

        Returns:
            list<str>: The names of the used terminals.
        """
        left = []
        right = []
        if self._left is not None:
            left = self._left.used_terminals
        if self._right is not None:
            right = self._right.used_terminals
        return left + right

    def __str__(self):
        """
        Return an neat string representation.

        Returns:
            str: The expression as a string.
        """
        str_rep = ''
        if self._left is not None:
            str_rep += str(self._left)
        if self._op[2]:
            str_rep += str(self._op[2])
        if self._right is not None:
            str_rep += str(self._right)
        if self._left is not None and self._right is not None:
            str_rep = '({})'.format(str_rep)
        return str_rep


class List(Node):
    """
    A node for evaluating a list of comma seperated expressions.
    """

    def _init(self, s):
        """
        Initialiser for the List class.

        Args:
            s (str): The string to parse.
        """
        super()._init()
        self._children = []
        for s_i in s.split(','):
            child = Expression(s_i)
            child._parent = self
            self._children.append(child)
            self.used_terminals.extend(child.used_terminals)

    def evaluate(self, mesh=None, V=None):
        """
        Evaluate the tree and return the correctly parsed equation.

        Args:
            mesh (Mesh):
                The firedrake mesh to evaluate the value for.
            V (FunctionSpace, optional):
                The firedrake functionspace that spatial coords will be
                evaluated over. Defaults to None.

        Returns:
            list<float, int, firedrake equation>:
                The parsed function for use with firedrake.
        """
        return [child.evaluate(mesh, V) for child in self._children]

    def __str__(self):
        """
        Return an neat string representation.

        Returns:
            str: The list as a string.
        """
        return '[' + ', '.join(str(c) for c in self._children) + ']'


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

    def _init(self, s):
        """
        Initialiser for the Terminal class.

        Args:
            s (str): The string to parse as a terminal.
        """
        super()._init()
        self._string = s.strip()
        if s in self._custom_terminals:
            self._used_terminals = [s]

        # Check if terminals have been added. If not, add them.
        if 'false' not in self._reserved_terminals:
            self._reserved_terminals.extend(
                ['false', 'true',
                 'x[0]', 'x[1]', 'x[2]',
                 'x', 'y', 'z'])

    def evaluate(self, mesh=None, V=None):
        """
        Evaluate the terminal and return the parsed value

        Args:
            mesh (Mesh, optional):
                The firedrake mesh to evaluate the value for.
                Defaults to None.
            V (FunctionSpace, optional):
                The firedrake functionspace that spatial coords will be
                evaluated over. Defaults to None.

        Returns:
            (varies): The parsed terminal.
        """
        if self._string in self._custom_terminals:
            return self._custom_terminals[self._string]

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

        if mesh is not None:
            x = SpatialCoordinate(mesh)
            str_to_spatial_coords_lookup = {
                'x': x[0],
                'x[0]': x[0]}
            if len(x) > 1:
                str_to_spatial_coords_lookup.update({
                    'y': x[1],
                    'x[1]': x[1]})
            if len(x) > 2:
                str_to_spatial_coords_lookup.update({
                    'z': x[2],
                    'x[2]': x[2]})

            if self._string in str_to_spatial_coords_lookup:
                sc = str_to_spatial_coords_lookup[self._string]
                return Function(V).interpolate(sc)

        return self._string.strip('"').strip("'")

    def __str__(self):
        return self._string


# pylint: disable=dangerous-default-value
def process_args(conf, factory=None, str_keys=['type'], clean=True):
    """
    Process the input config into a nested dictionary with evaluated values.
    Entries starting with an '_' are classed as interim functions and will not
    be returned, but will be used in returned values.

    Args:
        conf (dict):
            The dictionary to parse. Keys are expected to be strings with any
            nesting indicated by '.'s. Values should also be strings.
            e.g. {'arg_1.param': '2.0'}
        factory (FunctionBuilderFactory, optional):
            The factory that should be used to create any interim functions.
            Setting this to None indicates that no functions are expected.
            Defaults to None.
        str_keys (list, optional):
            The keys that are known to be strings and do not need parsing.
            Defaults to ['type'].
        clean (bool, optional):
            If True, clear all custom terminals before processing.
            Defaults to True.

    Returns:
        dict: A nested dictionary of all non-interim entries with parsed values
    """
    outputs = {}
    util_functions = {}
    if clean:
        Node.clear_terminals()

    mesh = factory.mesh if factory is not None else None
    V = factory.V if factory is not None else None

    tmp_functions = {k[1:].split('.')[0]
                     for k in conf
                     if k.startswith('_')}

    for f in tmp_functions:
        Node.subscribe_terminal(f)

    to_evaluate = []

    for k, v in conf.items():
        if k.startswith('_'):
            tmp_dict = util_functions
            k = k[1:]
        else:
            tmp_dict = outputs

        keys = k.lower().split('.')

        for key in keys[:-1]:
            if key not in tmp_dict:
                tmp_dict[key] = {}
            tmp_dict = tmp_dict[key]

        if keys[-1] not in str_keys:
            v = Expression(v)
            if v.ready():
                v = v.evaluate(mesh, V)
            else:
                to_evaluate.append((keys, v))

        tmp_dict[keys[-1]] = v

    # Worst case, need to do len(to_evaluate) attempts.
    for _ in range(len(to_evaluate) + 1):
        subscribed = []
        for k, v in util_functions.items():
            evaluated = []
            for i, (keys, expr) in enumerate(to_evaluate):
                if k == keys[0]:
                    if expr.ready():
                        tmp = v
                        val = expr.evaluate(mesh, V)
                        if len(keys) > 1:
                            for n in keys[1:-1]:
                                tmp = v[n]
                            tmp[keys[-1]] = val
                        else:
                            v = val
                        evaluated.append(i)
                    else:
                        break
            else:
                if isinstance(v, dict) and 'type' in v:
                    f_type = v.pop('type')
                    v = factory.create_function(f_type, **v)
                Expression.update_terminal(k, v)
                subscribed.append(k)

            to_evaluate = [v for i, v in enumerate(to_evaluate)
                           if i not in evaluated]

        util_functions = {k: v for k, v in util_functions.items()
                          if k not in subscribed}

    for keys, val in to_evaluate:
        tmp_dict = outputs
        for n in keys[:-1]:
            tmp_dict = tmp_dict[n]
        tmp_dict[keys[-1]] = val.evaluate(mesh, V)

    return outputs
