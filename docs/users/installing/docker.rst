

#############################################
Installing Firedrake - Docker (*recommended*)
#############################################

The easiest and fastest way to access firedrake is by using docker.
Docker is an open source software platform to create, deploy and manage
virtualized application containers. This effectively works like a
virtual machine.

The first step is to ensure docker is installe dby following the instructions
on their website `here <https://docs.docker.com/get-docker/>`__.

Once docker is available, the next step is getting the firedrake container,
which can easily be done using the pull command available
`here <https://hub.docker.com/r/firedrakeproject/firedrake/>`__.

Check this has been downloaded properly using::

  docker container list

There is now an image of the container for firedrake on the machine.
The final step in setting this up is to run the image as a container::

  docker run -i -d --name ttip firedrakeproject/firedrake

Here the ``-i`` and ``-d`` options stop the container from exiting immediately.

You should now have a running container on your system which you can log into
using::

  docker exec -it ttip /bin/bash


This docker container will persist as long as it is not deleted. If the container
not available (eg. after a restart) try using the folowing to restart where you
left off::

  docker start ttip
