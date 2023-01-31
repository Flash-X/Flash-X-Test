######################
 Example Instructions
######################

***************
 Regular Usage
***************

Use following steps to run the example on your local machine.

-  Initialize ``config`` and ``execfile``,

.. code::

   flashxtest init -z <pathToFlash> -s <flashSite> -a <pathToLocalArchive> -m <pathToMainArchive> -mpi <pathToMPI>

Note that options are not required for intialization, and can be
explicitly supplied by editing respective fields in your ``config`` and
``execfile``

-  Setup test suite

.. code::

   flashxtest setup-suite Example.suite

-  Run the test suite

.. code::

   flashxtest run-suite

Use ``--archive`` to save a tarball for the results to main archive

*******************************
 Setting Up Initial Benchmarks
*******************************

To setup initial benchmarks do the following after running ``flashxtest
init`` and ``flashxtest setup-suite``

-  Run the suite in with ``--set-benchmarks`` option

.. code::

   flashxtest run-suite --set-benchmarks

This will execute two consecutive runs for tests that do not contain
benchmark information, update ``test.info``, create a tarball of
results, and store it in main archive defined in ``pathToMainArchive``
in your ``config`` file

-  Check the suite

.. code::

   flashxtest check-suite Example.suite

This will check updates to ``test.info`` and tell you what values to set
for ``-cbase`` and ``-rbase`` in ``Example.suite``
