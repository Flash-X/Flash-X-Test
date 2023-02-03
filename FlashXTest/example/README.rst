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
 Setting Up Initial Benchmarks
*******************************

To setup initial benchmarks do the following after running ``flashxtest
init`` and ``flashxtest setup-suite``

-  Run the suite in with ``--create-benchmarks`` option

.. code::

   flashxtest run-suite --create-benchmarks

This option will pick ``Composite`` and ``Comparison`` tests from
``*.suite`` files that do not contain ``cbase`` and ``rbase`` values,
and run them. The initial run will fail, and a message will be display
stating the location of results. You can verify the results and accept
the run as new benchmark by simply setting ``-cbase
<yyyy-mm-dd>_[version]`` date string from the output message.

This will execute for tests that do not contain benchmark information,
update ``test.info``, create a tarball of results, and store it in main
archive defined in ``pathToMainArchive`` in your ``config`` file

-  Check the suite

.. code::

   flashxtest check-suite Example.suite

This will check updates to ``test.info`` and tell you what values to set
for ``-cbase`` and ``-rbase`` in ``Example.suite``
