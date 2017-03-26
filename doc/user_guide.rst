##########
User Guide
##########

============
Introduction
============

This document describes a suite of Python packages that facilitate the
implementation and deployment of dynamic filters and feedback
controllers.

The package is entirely written in `Python
<https://www.python.org>`_. We only support Python `Version 3
<https://wiki.python.org/moin/Python2orPython3>`_ and have no intent
to support Version 2.

Python is widely deployed and supported, with large amounts of
tutorials and documentation available on the web. A good resource to
start learning Python is the `Beginner's guide to Python
<https://wiki.python.org/moin/BeginnersGuide>`_.

All code should run on multiple desktop platforms, including Linux and
MacOSX. It has also been tested and deployed in the `Beaglebobe Black
<https://www.beagleboard.org/black>`_ and the `Raspberry Pi
<https://www.raspberrypi.org>`_. In particular we support the
`Robotics Cape <http://www.strawsondesign.com/>`_ and the `Beaglebone
Blue <https://beagleboard.org/blue>`_. See Section :ref:`Installation`
for details. 

============
Installation
============

The Python source code is available from:

* `ctrl <https://github.com/mauricio/ctrl>`_


---------------------
Robotics Cape support
---------------------

If you would like to run software on a `Beaglebobe Black
<https://www.beagleboard.org/black>`_ equipped with the `Robotics Cape
<http://www.strawsondesign.com/>`_ or the `Beaglebone Blue
<https://beagleboard.org/blue>`_ you might need to download and
install the Robotics Cape C library from:

* `Robotics Cape library <https://github.com/StrawsonDesign/Robotics_Cape_Installer>`_

Once you have the library installed and the cape running you should
also install our Python bindings available as:

* `rcpy package <https://github.com/mcdeoliveira/rcpy>`_
   
--------------------
Raspberry Pi support
--------------------

TODO 

.. include:: tutorial.inc

.. include:: advanced.inc
	     
.. include:: examples.inc

     
