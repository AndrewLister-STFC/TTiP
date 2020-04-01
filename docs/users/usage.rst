.. _file_usage:

##########
Using TTiP
##########

TTiP is controlled entirely by the problem definition config file and so
running the software is as easy as::

    ttip my_problem.ini

provided "my_problem.ini" is a correctly defined problem as per
:ref:`file_conf_file`.

Troubleshooting
===============

If the above does not work there are several things to check:

- The firedrake environment is active (usually this is shown in the terminal).
  If it is not, run::

    . <firedrake_dir>/bin/activate

  where `<firedrake_dir>` is the location of the firedrake installation.

- The "ttip" command has been installed correctly::

    ls <firedrake_dir>/bin/ttip

  If not try reinstalling as per instructions in :ref:`file_install`.
