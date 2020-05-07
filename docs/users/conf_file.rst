.. _file_conf_file:

##################
Configuration File
##################

Functions
=========
TTiP allows the creation of functions using either one of the built in function
builders, or by writing expressions.

The simplest functions can be defined as::

    <name>: <expression>

e.g.::

    radial: 1/sqrt(x^2 + y^2)

Functions can also be interim functions.
An interim function is one that is used as a component in other functions but
is not used directly by the section.
To define an interim function, start the function name with an '_'::

    _<name>: <expression>

Interim functions can then be used by name::

    _foo: 10 + x*y
    bar: foo^2

TTiP also offers predefined function builders which offer some useful
functionality.
Function builders are used to create specific functions in the TTiP
configuration file and are defined by setting the various properties with
respect to a name, using the form::

    <name>.<property>: <value>

Each function builder must define the `type` property, along with the relevent
properties for the selected type.
e.g.::

    foo.type: gaussian
    foo.mean: 0.5
    foo.sd: 0.1
    foo.scale: 10

Available function builders are:

- :ref:`sub_sub_condition`
- :ref:`sub_sub_constant`
- :ref:`sub_sub_gaussian`

.. _sub_sub_condition:

Condition
^^^^^^^^^

.. automodule:: TTiP.function_builders.condition_builder

.. _sub_sub_constant:

Constant
^^^^^^^^

.. automodule:: TTiP.function_builders.constant_builder

.. _sub_sub_gaussian:

Gaussian
^^^^^^^^

.. automodule:: TTiP.function_builders.gaussian_builder

File Sections
=============
Each section is defined properly in the example config:

.. include:: ../../TTiP/resources/default_config.ini
   :literal:

