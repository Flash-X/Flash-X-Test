######################
 Example Instructions
######################

***************
 Regular Usage
***************

Use following steps to run the example on your local machine.

-  Initialize ``config`` and ``execfile``,

.. code::

   ``flashxtest init -z <pathToFlash> -s <flashSite> -a <pathToLocalArchive> -m <pathToMainArchive> -mpi <pathToMPI>``

Note that options are not required for intialization, and can be
explicitly supplied by editing respective fields in your ``config`` and
``execfile``

-  Setup test suite

.. code::

   ``flashxtest setup-suite Example.suite``

-  Run the test suite

.. code::

   ``flashxtest run-suite``

*******************************
 Setting Up Initial Benchmarks
*******************************

To setup initial benchmarks do the following after running ``flashxtest
init`` and ``flashxtest setup-suite``

-  Run and archive the first run

.. code::

   ``flashxtest run-suite --archive``

This will create
