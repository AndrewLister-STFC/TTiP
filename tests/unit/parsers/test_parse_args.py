"""
Test for the parse_args.py file.
"""

from unittest import TestCase

from firedrake import UnitCubeMesh, Function, FunctionSpace
from numpy import isclose
from pytest import mark

from TTiP.parsers.parse_args import (Expression, List, Node, Terminal,
                                     process_args)

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
                   ('-8e-2 * -100', 8),
                   ('2^2', 4),
                   ('((8-13e-1)*(1e1+1-2/2)+(4-2)^2-3^(1+3))*-0.1', 1)])
def test_expressions(expr_str, expr_val):
    """
    Test that a variety of expressions are correctly parsed.
    """
    expr = Expression(expr_str).evaluate()
    assert isclose(expr, expr_val)


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
    pass
