
###############
Installing TTiP
###############

First ensure you have access to the source code::

  git clone https://github.com/AndrewLister-STFC/TTiP.git
  cd TTiP

The next step is to ensure it will be installed with access to firedrake.
To do this, activate the firedrake virtual environment::

  . firdrake/bin/activate

Once inside the firedrake virtualenv, install any additional packages that are
required with (in the root of this repository)::

    pip install .


To check it works, try running::

    ttip --help
