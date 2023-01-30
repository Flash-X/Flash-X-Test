##############
 Flash-X-Test
##############

|Code style: black|

This repository contains source code for the command line toolkit for
maintaining Flash-X testing infrastructure. Most of the documentation
for usage can be accessed using the ``--help`` option after successful
installation of the application. The documentation here provides
instructions for installation and a guide for developers who wish to
contribute to the functionality of the toolkit.

``FlashXTest`` is a user-friendly wrapper over the legacy ``FlashTest`` and
``FlashTestView`` applications that have been used before for managing
regular testing during  development of
FLASH and Flash-X.

Note that Flash-X-Test depends on ``Python3+``, and consequently ``pip``
should point to ``Python3+`` installation package ``pip3``.

**************
 Installation
**************

Stable releases of Flash-X-Test are available as tags attached to this
repository (https://github.com/Flash-X/Flash-X-Test/tags) and can be
installed by executing,

.. code::

   pip install git+ssh://git@github.com/Flash-X/Flash-X-Test.git@<tag> --user

Upgrading and uninstallation is easily managed through this interface
using,

.. code::

   pip install --upgrade git+ssh://git@github.com/Flash-X/Flash-X-Test.git@<tag> --user
   pip uninstall FlashXTest

It is recommended to install in ``--user`` mode to avoid root privilege
issues with ``pip``.

``FlashXTest`` provides both Command Line Interface (CLI) and Python
Application Programming Interface (API). The CLI script, ``flashxtest``,
is copied to the ``$HOME/.local/bin`` directory, and therefore the
``PATH`` variable should be updated to allow running ``flashxtest`` as a
shell command.

The Python API can be accessed directly without any ``PATH``
modifications by simply importing the module as,

.. code::

   import FlashXTest

The CLI is a mirror of the Python API, and therefore commands and
functionality are exactly similar between the two. This provides users a
choice to either use CLI interactively or integrate with other Python
workflows using the API.

*****************
 Developer Guide
*****************

There maybe situations where users may want to install ``FlashXTest`` in
development mode $\\textemdash$ to design new features, debug, or
customize classes/methods to their needs. This can be easily
accomplished using the ``setup`` script located in the project root
directory and executing,

.. code::

   ./setup develop

Development mode enables testing of features/updates directly from the
source code and is an effective method for debugging. Note that the
``setup`` script relies on ``click``, which can be installed using,

.. code::

   pip install click

The ``./setup`` script should be run in the project root directory. It
mimics the pip installation but creates ``egg-link`` to project root
directory to allow for code development and debugging.

Please read ``DESIGN.rst`` to understand software design logic before
contributing to the code

*******
 Usage
*******

Once ``FlashXTest`` is configured using the installation instructions,
the CLI documentation can be accessed using,

.. code::

   flashxtest --help

For documentation for individual commands use following,

.. code::

   flashxtest <command> --help

Version of the current installation can be infered with,

.. code::

   flashxtest --version

An example of a test suite is provided under ``FlashXTest/example``
please refer to the instructions there to understand how to setup a test
suite.

****************
 Help & Support
****************

Please file an issue on the repository page

.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
