.. _func_builders:

Function Builders
=================

The function builders can be found in the `function_builders` directory
alongside a base class and a factory implementation.

Base Class (``function_builder.py``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The base class defines some shared interfaces for all of the function builders,
and should be inheritted from for a new function builder to work.

In general, the only requirement for the sub classes of this are that they
override the abstract ``build`` method so that it returns a firedrake Function,
or a numerical value.
In practice, since this is designed to only be accessed by the factory
(explained below), there are additional constraints:

- Function builders should not modify the signature of ``__init__``.
  E.g. they are initialised with ``(mesh, V)`` and any other arguments must be
  defined using the assign method.

- The signature of build should not be edited. To access arguments for
  constructing a function, the object dictionary ``_props`` should be used.


Since the build method signature cannot be changed, values must be passed
through a different mechanism.
This is done using the ``_props`` dictionary and ``assign`` method.

Assign takes a `name` and a `value` as inputs, it then checks this pair is
valid for the class by checking that the `name` is in the ``properties``
dictionary and that the type of `value` matches the entry in ``properties``.
If it is valid, ``_props`` is updated with the `name`-`value` pair.

Factory (``function_builder_factory.py``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The factory is used to dynamically import and use only the specified function
builder at runtime.
This means that extending the set of function builders is done by creating a
new file. The factory will then be able to find the new builder by name and
load the code.

In order for the factory to work, there can only be 1 function builder per
file.

Function Builders (``<type>_builder.py``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The rest of the files in this directory are function builders and should serve
as good examples for adding new ones.

To create a new function builder, you should make sure to define the following
on the new subclass:

- ``properties`` dict: This dictionary should have the names of all properties
  that are required to build a function, alongside the type of each property.
  Types can be specified as a tuple e.g. if a value can be `int` or `float`.

- ``build`` method: This is the main logic in the builder.

It is also important to name the file sensibly as this is how the function
builder will be selected. For a file called ``foo_builder.py``, the user will
be required to set the type in the config file to ``foo``. If this is not
appropriate in the future, the factory will have to be changed.
