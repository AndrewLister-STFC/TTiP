
#############################
Installing Firedrake - Manual
#############################

*Warning: This method will take a long time to install*

TTiP uses `Firedrake <https://firedrakeproject.org/index.html>`__
to solve the underlying equations. To install this, please see the install page
in their documentation `here <https://firedrakeproject.org/download.html>`__.

Firedrake in turn uses the widely used PETSc which will be installed with
Firedrake but can take some time.

It is recommended to use the default install for this, which will create a
directory called "firedrake" where all the necessary packages can be found.
In particular this contains a virtualenv which will be required to run TTiP.

To activate the virtualenv run::

    . firedrake/bin/activate

This will mean python can access the firedrake modules.