######################
 Example Instructions
######################

***************
 Regular Usage
***************

Use following steps to run the example on your local machine.

-  Initialize ``config`` and ``execfile``,

.. code::

   flashxtest init

   options:
   -z <pathToFlash>
   -s <flashSite>
   -a <pathToLocalArchive>
   -m <pathToMainArchive>
   -o <pathToOutdir>
   -mpi <pathToMPI>
   -make "<pathToMake> -j<numJobs>"

Note that options are not required for intialization, and can be
explicitly supplied by editing respective fields in your ``config`` and
``execfile``

-  Setup ``test.info`` using all ``*.suite`` files in your working
   directory. The ``*.suite`` represent a collection of mutually
   exclusive tests that can be organized based on your preference. Use
   ``--help`` to see more documentation.

.. code::

   flashxtest setup-suite

When ``test.info`` is alredy present in the working directory, this
command will ask for confirmation to overwrite it. To enable explicit
overwrite, use ``--overwrite`` option.

-  Run the test suite

.. code::

   flashxtest run-suite

Use ``--archive`` to save a tarball for the results to main archive

*******************************
 Setting Up Benchmarks
*******************************

To setup initial benchmarks do the following after running ``flashxtest
init`` and ``flashxtest setup-suite``

-  Run the suite in with ``--archive`` option

.. code::

   flashxtest run-suite --archive

The initial run will fail, and messages will be displayed
stating the location of results and recommendations for ``cbase`` values in ``*.suite`` files.
The messages can also be view in ``flashxtest_api.log``.

Here is an example output from ``flashxtest_api.log``

.. code::

   --------------------------------------------------------------------------------
   WARNING: Verify results in - /home/akash/jobs/flash-x-testing/TestResults/sedona/2023-02-03
   --------------------------------------------------------------------------------
   NOTE!    Suggested changes to "*.suite" files:
   NOTE!    Set "cbase" to "2023-02-03" for "Comparison/Sod/UG/2d/simpleUnsplit"
   NOTE!    Set "cbase" to "2023-02-03" for "Composite/Sod/PseudoUG/2d/Paramesh/simpleUnsplit"
   --------------------------------------------------------------------------------

-  Check the suite

.. code::

   flashxtest check-suite Example.suite

This will check updates to ``test.info`` and tell you what values to set
for ``-cbase`` and ``-rbase`` in ``Example.suite``
