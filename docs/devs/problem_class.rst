.. _problem_class:

Problem Class
=============

The problem definitions in TTiP are designed to be extensible, this is done
through multiple inheritance and mixin classes.

The two main parts to a problem class in TTiP are the base class and the
mixins.

Base Class
^^^^^^^^^^
The base class (found in ``core/problem.py``) defines a set of methods that
create, set (replace), and bound firedrake functions. It also defines a set of
functions such as the flux and ionisation terms which are used in multiple
mixins.

The formula that the problem defines is given by:

.. math::

   a - L = 0

:math:`a` is the sum of terms containing both :math:`T` and :math:`v`, whereas
:math:`L` does not contain :math:`T` explicitly (some parameters can be
dependant on temperature). 

Mixins
^^^^^^
The mixins are fundamental to creating a sensible problem.

A variety of mixins can be found in the ``problem_mixins`` directory.

Mixins are used to add functionality such as time dependancies, flux limits,
specific conductivity formulations, and many others.

The key concept of a mixin for the problem class is that it should edit the
existing variables rather than replacing them, either by adding terms or by
using the ``set_function`` method from the parent class (which will be
available at runtime as the mixin will only ever be used with the base problem
class). Some examples of this are the time dependancy mixin which adds a term
to the ``a`` attribute, and the conductivity limiter which imposes bounds on
the existing conductivity.

Usage
^^^^^
Some examples of how to define new problem classes can be seen at the bottom of
the ``core/problem.py`` file as well as a utility function to dynamically
create new problem classes.

Extending
^^^^^^^^^
To add new functionality to the problem class, define a new mixin (using the
template in ``problem_mixins``) this can then be used in any custom scripts.
To make the new mixin more accessible, it should be added to the
``create_problem_class`` method in the problem file.
