

Code Structure
==============

The source code for TTiP is structured into the following sections:

- *cli*: Entry points to the software.

- *core*: Main functionality.

- *function_builders*: Classes to create functions from config inputs.

- *parsers*: Code for parsing the config file.

- *problem_mixins*: Extensions for the problem class.

- *resources*: Any non code assets.

- *util*: Generic code that is used in various other places.

More detail on these can be found below.

CLI
^^^
The cli is designed be the main access point for TTiP from the terminal.
Currently this only includes a single file which serves as the main entry
point for the software.

Core
^^^^
The core folder contains code that is central to the logic of TTiP and ties
the other section together. This includes the solver, base problem, and
the interface to the parsers.

Function Builders
^^^^^^^^^^^^^^^^^
The function builders folder follows a factory design pattern.
This folder holds the factory and all of the function builders.
More information on this can be found in :ref:`func_builders`.

Parsers
^^^^^^^
The parsers folder holds all code related to parsing the config file.
This includes a file for each section of the config file, as well as a
base class and argument parser.
More information can be found in :ref:`conf_parsing` and :ref:`expr_parsing`.

Problem Mixins
^^^^^^^^^^^^^^
The problem mixins directory holds all optional extensions for the problem
class.
Information on these mixins is in :ref:`problem_class`.

Resources
^^^^^^^^^
The resources directory is a place to store assets that are not source code.
Currently the only file in this directory is a default config file which also
serves to document the config options for a user.

Util
^^^^
Finally, the util directory is a place for anything that doesn't obviously fit
in the other directories. This is likely to be any utility methods or
functionality.
Currently this only holds some code to setup a logger.
