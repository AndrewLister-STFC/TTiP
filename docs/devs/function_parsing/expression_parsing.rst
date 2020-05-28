.. _expr_parsing:

Expression Parsing
==================

The expression parser can be found in ``parsers/parse_args.py``.

This works by reading the expression from left to right and building a tree
which is evaluated once complete. For example::

    x + 2*y :=    +
                 / \
                x   *
                   / \
                  2   y

The expression parser is made up of Node subclasses: Expression, List, and
Terminal.

Base Node
^^^^^^^^^
The base class contains code to return the parent node when created.

Due to the way this works, the tree is built up in both directions.
As such, when creating a node from a string, the root node should be returned.
This is done by overriding ``__new__`` and using a custom initialiser ``_init``
rather than the usual ``__init__`` (using the standard initialiser causes
objects to be reinitialised after ``__new__``).

The base node also controls named terminals for the expression parser.
This allows custom terminals, where a name is given to the parser from the
calling code alongside a value, and reserved terminals, where the name is
reserved for use by one of the Node classes (e.g. 'false').

Finally, the base node also has the functionality to return a ready state
describing if it can be evaluated yet. A node is considered to be ready if all
the required terminals in custom_terminals have been assigned a value.

Expression
^^^^^^^^^^
The Expression class handles the bulk of the tree building, and within, this is
done on initialisation (in the ``_init`` method).

In brief, this class takes a string and determines the next operator, it then
creates a new tree for each of the left and right operands.
If the operator has a lower or equal priority than the parents operator, a
pivot is applied.

The pivot follows the following pattern::

      op1                op2
     /   \              /   \
    x    op2    ->    op1    z
        /   \        /   \
       y     z      x     y

Where x, y, and z can also be a tree.

The operands are defined by a dictionary at the class level which maps the
string format to a tuple of priority, callable, and string format.

Expressions can also contain unary functions defined in the functions
dictionary. These are called by a name followed by an open bracket
(except in the case of negation).

New binary functions should be added by extending the operators dictionary and
new unary functions should be added by extendin the functions dictionary.

Evaluation of an expression is done by first evaluating a left and right hand
side, then applying an operator to them.

List
^^^^
The list node is used for any string with a comma in.
It assumes that the string is a comma separated list and creates an expression
for each of these.

Terminal
^^^^^^^^
Terminal nodes evaluate the singleton values after operators have been removed.
This includes boolean, integer, float, string, and coordinate values.

Coordinate values are reserved keyword mappings that allow for expressions such
as::

   x^2 + y^2

Where x and y are the mesh coordinates.
