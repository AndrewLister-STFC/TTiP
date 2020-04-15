.. _file_conf_file:

##################
Configuration File
##################

Functions
=========
Functions in the TTiP configuration file are defined by setting the various
properties with respect to a name, using the form::

    <name>.<property>: <value>

Each function must define the `type` property, along with the relevent
properties for the selected type.

Available function types are:

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

