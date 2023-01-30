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

*******************************
 Setting Up Initial Benchmarks
*******************************

To setup initial benchmarks do the following after running ``flashxtest
init`` and ``flashxtest setup-suite``

-  Run the suite in with ``--initial`` option

.. code::

   flashxtest run-suite --initial

This will execute two consecutive runs, update ``test.info``, and create
a tarball of your results, and store it in main archive defined in
``pathToMainArchive`` in your ``config`` file

-  Next update ``Example.suite`` to set ``-cbase <yyyy-mm-dd>`` and
   ``-rbase <yyyy-mm-dd>_2`` to create a tag for comparison and restart
   benchmarks for subsquent test suite runs, so that new ``test.info``
   contains correct values for benchmarks
