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

``flashxtest`` is a user-friendly wrapper over legacy FlashTest and
FlashTestView applications that have been succesffuly used before for
managing FLASH and Flash-X development.

Note that Flash-X-Test depends on ``python3+`` and consquently ``pip``
should point to ``python3+`` installation package ``pip3``.

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

*****************
 Developer Guide
*****************

There maybe situations where users may want to install BoxKit in
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

*******
 Usage
*******

****************
 Help & Support
****************

Please file an issue on the repository page

.. |Code style: black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
