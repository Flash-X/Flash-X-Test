######################
 Example Instructions
######################

***************
 Regular Usage
***************

Use following steps to run the example on your local machine.

-  Initialize ``config`` and ``execfile``,

.. code::

   flashxtest init -z <pathToFlash> \
                   -s <flashSite> \
                   -a <pathToLocalArchive> \
                   -m <pathToMainArchive> \
                   -o <pathToOutdir> \
                   -mpi <pathToMPI> \
                   -make "<pathToMake> -j<numJobs>"

Note that options are not required for intialization, and can be
explicitly supplied by editing respective fields in your ``config`` and
``execfile``

-  Setup ``test.info`` using all ``*.suite`` files in your working
   directory. The ``*.suite`` represent a collection of mutually
   exclusive tests that can be organized based on your preference. Use
   ``--help`` to see more documentation.

.. code::

   flashxtest setup-suite Example.suite

When ``test.info`` is alredy present in the working directory, this
command will ask for confirmation to overwrite it. To enable explicit
overwrite, use ``--overwrite`` option.

-  Run the test suite

.. code::

   flashxtest run-suite

Use ``--archive`` to save a tarball for the results to main archive

***********************
 Setting Up Benchmarks
***********************

To setup initial benchmarks do the following after running ``flashxtest
init`` and ``flashxtest setup-suite Example.suite``

-  Run the suite in with ``--archive`` option

.. code::

   flashxtest run-suite --archive

-  The initial run will fail due to missing values of ``cbase`` and
   ``rbase`` values. These values can be added to the suite file using

.. code::

   flashxtest add-cbase Example.suite <YYYY-MM-DD>

-  Next, setup and run test suite again

.. code::

   flashxtest setup-suite --overwrite Example.suite
   flashxtest run-suite --archive

-  If transparent restart passes for ``Composite`` tests, then this run
   will be succesfull, if not manually verify restart benchmarks and
   them to suite file

.. code::

   flashxtest add-cbase Example.suite <YYYY-MM-DD>_2

Your test suite is now setup for production runs. You can use the
commands above to manage it as your tests change.
