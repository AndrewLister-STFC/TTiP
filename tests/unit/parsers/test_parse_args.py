"""
Test for the parse_args.py file.
"""

from unittest import TestCase

from firedrake import Function, FunctionSpace, UnitCubeMesh
from numpy import isclose
from pytest import mark

from TTiP.function_builders.function_builder_factory import \
    FunctionBuilderFactory
from TTiP.parsers.parse_args import (Expression, List, Node, Terminal,
                                     process_args)

# pylint: disable=attribute-defined-outside-init, protected-access

# =============================================================================
# ========== Node Class =======================================================
# =============================================================================


class DummyNode(Node):
    """
    Dummy class to instantiate minimal Node.
    """

    def evaluate(self, mesh=None, V=None):
        """
        Override for abstract class.
        """
        return 1


class TestReady(TestCase):
    """
    Tests for the Node.ready method.
    """
    @classmethod
    def setUpClass(cls):
        """
        Define custom terminals.
        """
        Node._custom_terminals = {'foo': None,
                                  'bar': 2.0,
                                  'baz': 3}

    def setUp(self):
        """
        Create an instantiated node.
        """
        self.node = DummyNode()

    @classmethod
    def tearDownClass(cls):
        """
        Clear the custom terminals.
        """
        Node._custom_terminals = {}

    def test_no_used_terminals(self):
        """
        Test that ready is true if no custom terminals are used.
        """
        self.node._used_terminals = []
        self.assertTrue(self.node.ready())

    def test_use_undefined_terminals(self):
        """
        Test that ready is false if terminals are not defined.
        """
        self.node._used_terminals = ['foo']
        self.assertFalse(self.node.ready())

    def test_use_mix_terminals(self):
        """
        Test that ready is false if one of the terminals is not defined.
        """
        self.node._used_terminals = ['foo', 'bar']
        self.assertFalse(self.node.ready())

    def test_use_defined_terminals(self):
        """
        Test that ready is true if terminals are all defined.
        """
        self.node._used_terminals = ['bar', 'baz']
        self.assertTrue(self.node.ready())


class TestClearTerminals(TestCase):
    """
    Tests for the Node.clear_terminals method.
    """
    @classmethod
    def setUpClass(cls):
        """
        Define custom terminals.
        """
        Node._custom_terminals = {'foo': None,
                                  'bar': 2.0,
                                  'baz': 3}

    def setUp(self):
        """
        Create an instantiated node.
        """
        self.node = DummyNode()

    @classmethod
    def tearDownClass(cls):
        """
        Clear the custom terminals.
        """
        Node._custom_terminals = {}

    def test_clears_custom_terminals(self):
        """
        Test that clear_terminals clears all terminals.
        """
        self.assertNotEqual(Node._custom_terminals, {})
        self.node.clear_terminals()
        self.assertEqual(Node._custom_terminals, {})


class TestSubscribeTerminal(TestCase):
    """
    Tests for the Node.subscribe_terminals method.
    """
    @classmethod
    def setUpClass(cls):
        """
        Define custom terminals.
        """
        Node._custom_terminals = {}

    def setUp(self):
        """
        Create an instantiated node.
        """
        self.node = DummyNode()

    @classmethod
    def tearDownClass(cls):
        """
        Clear the custom terminals.
        """
        Node._custom_terminals = {}

    def test_subscribe_terminal_no_value(self):
        """
        Test that subscribing a terminal with no value works.
        """
        self.assertNotIn('foo', Node._custom_terminals)
        self.node.subscribe_terminal('foo')
        self.assertIn('foo', Node._custom_terminals)
        self.assertIs(None, Node._custom_terminals['foo'])

    def test_subscribe_terminal_with_value(self):
        """
        Test that subscribing a terminal with a value works.
        """
        self.assertNotIn('bar', Node._custom_terminals)
        self.node.subscribe_terminal('bar', 7.1)
        self.assertIn('bar', Node._custom_terminals)
        self.assertEqual(7.1, Node._custom_terminals['bar'])

    def test_subscribe_existing_terminal(self):
        """
        Test that an error is raised if the terminal already exists.
        """
        self.assertNotIn('baz', Node._custom_terminals)
        self.node.subscribe_terminal('baz')
        with self.assertRaises(AttributeError):
            self.node.subscribe_terminal('baz')


class TestUpdateTerminal(TestCase):
    """
    Tests for the Node.subscribe_terminals method.
    """
    @classmethod
    def setUpClass(cls):
        """
        Define custom terminals.
        """
        Node._custom_terminals = {}

    def setUp(self):
        """
        Create an instantiated node.
        """
        self.node = DummyNode()

    @classmethod
    def tearDownClass(cls):
        """
        Clear the custom terminals.
        """
        Node._custom_terminals = {}

    def test_update_non_existing_terminal(self):
        """
        Test that an error is raised if the terminal does not exist.
        """
        self.assertNotIn('foo', Node._custom_terminals)
        with self.assertRaises(AttributeError):
            self.node.update_terminal('foo', 6)

    def test_update_existing_terminal(self):
        """
        Test that updating a terminal works.
        """
        Node._custom_terminals['bar'] = 6.2
        self.node.update_terminal('bar', 5.9)
        self.assertEqual(Node._custom_terminals['bar'], 5.9)


# =============================================================================
# ========== Expression Class =================================================
# =============================================================================
@mark.parametrize('expr_str, expr_val',
                  [('1 + 1', 2),
                   ('2 - 1', 1),
                   ('2 * 2', 4),
                   ('4 / 2', 2),
                   ('1.5 + 3', 4.5),
                   ('2.9e2', 290),
                   ('-1 + 5', 4),
                   ('2 * 3 * 4', 24),
                   (' 1 - 2 - 3 ', -4),
                   ('1 - (2 - 3)', 2),
                   ('1 / 2 / 3', 1/6),
                   ('1 / 2 / 3 / 4', 1/24),
                   ('2 + 2 / 4 + 1 / 2', 3.0),
                   ('-8e-2 * -100', 8),
                   ('2^2', 4),
                   ('((8-13e-1)*(1e1+1-2/2)+(4-2)^2-3^(1+3))*-0.1', 1)])
def test_expressions(expr_str, expr_val):
    """
    Test that a variety of expressions are correctly parsed.
    """
    expr = Expression(expr_str).evaluate()
    assert isclose(expr, expr_val)

@mark.parametrize('expr_str, expr_val',
                  [('1 + 1', '(1+1)'),
                   ('2 - 1', '(2-1)'),
                   ('2 * 2', '(2*2)'),
                   ('4 / 2', '(4/2)'),
                   ('1.5 + 3', '(1.5+3)'),
                   ('2.9e2', '(2.9e2)'),
                   ('-1 + 5', '(-1+5)'),
                   ('2 * 3 * 4', '((2*3)*4)'),
                   (' 1 - 2 - 3 ', '((1-2)-3)'),
                   ('1 - (2 - 3)', '(1-(2-3))'),
                   ('1 / 2 / 3', '((1/2)/3)'),
                   ('1 / 2 / 3 / 4', '(((1/2)/3)/4)'),
                   ('2 + 2 / 4 + 1 / 2', '((2+(2/4))+(1/2))'),
                   ('-8e-2 * -100', '((-8e-2)*-100)'),
                   ('2^2', '(2^2)')])
def test_expression_str(expr_str, expr_val):
    """
    Test that a variety of expressions are correctly parsed.
    """
    expr = Expression(expr_str)
    assert str(expr) == expr_val

class TestUsedTerminals(TestCase):
    """
    Tests for the used_terminals property.
    """
    @classmethod
    def setUpClass(cls):
        """
        Add some custom terminals.
        """
        Expression.clear_terminals()
        Expression.subscribe_terminal('foo')
        Expression.subscribe_terminal('bar')

    @classmethod
    def tearDownClass(cls):
        """
        Clear the terminals.
        """
        Expression.clear_terminals()

    def test_no_terminals(self):
        """
        Test used terminals is empty when no terminals are used.
        """
        expr = Expression('1 + 2')
        self.assertListEqual([], expr.used_terminals)

    def test_with_one_terminal(self):
        """
        Test used terminals is populated when a terminal is used.
        """
        expr = Expression('foo * 2')
        self.assertListEqual(['foo'], expr.used_terminals)

    def test_with_two_terminal(self):
        """
        Test used terminals is populated when multiple terminals are used.
        """
        expr = Expression('foo * (1 + bar)')
        self.assertListEqual(['foo', 'bar'], expr.used_terminals)


# =============================================================================
# ========== List Class =======================================================
# =============================================================================


class TestList(TestCase):
    """
    Tests for the List class.
    """

    def test_create_list(self):
        """
        Test a list is created with parsed values.
        """
        list_str = '0.1, 3, foo'
        list_val = [0.1, 3, 'foo']
        self.assertListEqual(list_val, List(list_str).evaluate())


# =============================================================================
# ========== Terminal Class ===================================================
# =============================================================================


class TestTerminal(TestCase):
    """
    Test that terminals are evaluated correctly.
    """

    def tearDown(self):
        """
        Ensure no remaining terminals.
        """
        Node.clear_terminals()

    def test_bool_true(self):
        """
        Test true is correctly parsed.
        """
        self.assertTrue(Terminal('true').evaluate())

    def test_bool_false(self):
        """
        Test false is correctly parsed.
        """
        self.assertFalse(Terminal('false').evaluate())

    def test_spatial_coord_x(self):
        """
        Test spatial coords are correctly parsed.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)

        x = Terminal('x').evaluate(mesh, V)
        self.assertIsInstance(x, Function)
        self.assertAlmostEqual(x([0.12, 0.84, 0.61]).item(), 0.12)

    def test_spatial_coord_x_0(self):
        """
        Test spatial coords are correctly parsed.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)

        x = Terminal('x[0]').evaluate(mesh, V)
        self.assertIsInstance(x, Function)
        self.assertAlmostEqual(x([0.12, 0.84, 0.61]).item(), 0.12)

    def test_spatial_coord_y(self):
        """
        Test spatial coords are correctly parsed.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)

        x = Terminal('y').evaluate(mesh, V)
        self.assertIsInstance(x, Function)
        self.assertAlmostEqual(x([0.12, 0.84, 0.61]).item(), 0.84)

    def test_spatial_coord_x_1(self):
        """
        Test spatial coords are correctly parsed.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)

        x = Terminal('x[1]').evaluate(mesh, V)
        self.assertIsInstance(x, Function)
        self.assertAlmostEqual(x([0.12, 0.84, 0.61]).item(), 0.84)

    def test_spatial_coord_z(self):
        """
        Test spatial coords are correctly parsed.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)

        x = Terminal('z').evaluate(mesh, V)
        self.assertIsInstance(x, Function)
        self.assertAlmostEqual(x([0.12, 0.84, 0.61]).item(), 0.61)

    def test_spatial_coord_x_2(self):
        """
        Test spatial coords are correctly parsed.
        """
        mesh = UnitCubeMesh(10, 10, 10)
        V = FunctionSpace(mesh, 'CG', 1)

        x = Terminal('x[2]').evaluate(mesh, V)
        self.assertIsInstance(x, Function)
        self.assertAlmostEqual(x([0.12, 0.84, 0.61]).item(), 0.61)

    def test_float(self):
        """
        Test that floats are correctly parsed.
        """
        self.assertAlmostEqual(3.1, Terminal('3.1').evaluate())

    def test_int(self):
        """
        Test that ints are correctly parsed.
        """
        self.assertEqual(5, Terminal('5').evaluate())

    def test_str(self):
        """
        Test that strings are correctly parsed.
        """
        self.assertEqual('foo', Terminal('foo').evaluate())

    def test_custom_terminal(self):
        """
        Test that custom terminals are correctly parsed.
        """
        Node.subscribe_terminal('foo', 3)
        self.assertEqual(Terminal('foo').evaluate(), 3)
        Node.clear_terminals()


# =============================================================================
# ========== Non Class Methods ================================================
# =============================================================================


class TestProcessArgs(TestCase):
    def setUp(self):
        self.mesh = UnitCubeMesh(10, 10, 10)
        self.V = FunctionSpace(self.mesh, 'CG', 1)
        self.factory = FunctionBuilderFactory(self.mesh, self.V)

    def test_dict_with_only_values(self):
        conf = {'test': '3.0',
                'foo': 'false'}

        expected = {'test': 3.0,
                    'foo': False}

        args = process_args(conf)
        self.assertDictEqual(args, expected)

    def test_nested_values(self):
        conf = {'test.a': '3.0',
                'test.b': '4.1',
                'foo.b': 'false'}

        expected = {'test': {'a': 3.0,
                             'b': 4.1},
                    'foo': {'b': False}}

        args = process_args(conf)
        self.assertDictEqual(args, expected)

    def test_dict_with_functions(self):
        conf = {'test.type': 'constant',
                'test.value': '4.1',
                'foo.type': 'gaussian',
                'foo.scale': '10',
                'foo.mean': '0.5',
                'foo.sd': '0.5'}

        expected = {'test': {'type': 'constant',
                             'value': 4.1},
                    'foo': {'type': 'gaussian',
                            'scale': 10,
                            'mean': 0.5,
                            'sd': 0.5}}

        args = process_args(conf)
        self.assertDictEqual(args, expected)

    def test_dict_with_interim_values(self):
        conf = {'test': 'foo + 1',
                '_foo': '2.0'}

        expected = {'test': 3.0}

        args = process_args(conf)
        self.assertDictEqual(args, expected)

    def test_dict_with_interim_functions(self):
        conf = {'test': 'foo + 2.0',
                '_foo.type': 'gaussian',
                '_foo.scale': '10',
                '_foo.mean': '0.5',
                '_foo.sd': '0.5'}

        args = process_args(conf, self.factory)
        self.assertListEqual(list(args.keys()), ['test'])
        self.assertAlmostEqual(args['test']([0.5, 0.5, 0.5]).item(), 12.0)

    def test_dict_with_many_interim_values(self):

        conf = {'test': 'foo + 1',
                '_foo': 'bar + baz',
                '_bar': '17.0',
                '_baz': 'bar * 2'}

        expected = {'test': 17.0 + (17.0 * 2) + 1}

        args = process_args(conf)
        self.assertDictEqual(args, expected)

    def test_str_keys_arg(self):

        conf = {'test': 'foo + 1',
                'test2': '2.0'}

        expected = {'test': 'foo + 1',
                    'test2': 2.0}

        args = process_args(conf, str_keys=['test'])
        self.assertDictEqual(args, expected)

    def test_clean_arg_false(self):
        conf = {'_foo': '2.0',
                '_bar': '1.0'}
        args = process_args(conf)

        conf = {'test': 'foo + bar'}
        args = process_args(conf, clean=False)

        expected = {'test': 3.0}

        self.assertDictEqual(args, expected)

    def test_clean_arg_true(self):
        conf = {'_foo': '2.0',
                '_bar': '1.0'}
        args = process_args(conf)

        conf = {'test': 'foo + bar'}
        args = process_args(conf, clean=True)

        expected = {'test': 'foobar'}

        self.assertDictEqual(args, expected)
