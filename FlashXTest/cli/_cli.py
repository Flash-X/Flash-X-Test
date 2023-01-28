"""Python CLI for flashxtest"""

import os
import subprocess
import click
import pkg_resources

from .. import api


@click.group(name="flashxtest", invoke_without_command=True)
@click.pass_context
@click.option("--version", "-v", is_flag=True)
def flashxtest(ctx, version):
    """
    \b
    Command line interface for managing
    Flash-X testing framework. Type --help
    for individual commands to learn more.
    """
    if ctx.invoked_subcommand is None and not version:
        subprocess.run(
            f"export PATH=~/.local/bin:/usr/local/bin:$PATH && flashxtest --help",
            shell=True,
            check=True,
        )

    if version:
        click.echo(pkg_resources.require("FlashXTest")[0].version)


@flashxtest.command(name="init")
@click.option("--source", "-z", default=None, help="Flash-X source directory")
@click.option("--site", "-s", default=None, help="Flash-X site name")
@click.option("--local-archive", "-a", default=None, help="Path to local archive")
@click.option("--main-archive", "-m", default=None, help="Path to main archive")
@click.option("--mpi-path", "-mpi", default="mpiexec", help="Name for MPI executable")
def init(source, site, local_archive, main_archive, mpi_path):
    """
    \b
    Initialize site specific configuration.

    \b
    This command is used to setup site specific
    configuration for your testing environment
    using "config" and "execfile".

    \b
    This command will not replace exisiting
    "config" or "execfile" in the working 
    directory. To edit existing site specific 
    configuration, "config" and "execfile"
    should be edited directly.
    """
    # Arguments
    # ---------
    # source: Flash-X source directory
    # site: Flash-X site name
    if (not source) or ("$PWD" in source) or ("$pwd" in source):
        source = os.getcwd()
    if not local_archive:
        local_archive = os.getcwd() + "/TestLocalArchive"
    if not main_archive:
        main_archive = os.getcwd() + "/TestMainArchive"

    api.init(
        flashSite=site,
        pathToFlash=source,
        pathToLocalArchive=local_archive,
        pathToMainArchive=main_archive,
        pathToMPI=mpi_path,
    )


@flashxtest.command(name="setup-suite")
@click.argument("suitelist", type=str, nargs=-1)
def setup_suite(suitelist):
    """
    \b
    Create a "test.info" from a list of suite files.

    \b
    This command accepts multiple files with suffix,
    ".suite" to build a "test.info". If no arguments are
    supplied, all "*.suite" files are used from the working
    directory.

    \b
    The ".suite" files represent a collection of mutually
    exclusive test specifications associated with a "config" file.
    Each line in a file represent a unique test specification
    defined as,

    \b
        incompFlow/LidDrivenCavity -t "UnitTest/LidDrivenCavity/AMReX/2d" -np 4 --debug
    \b
        Sod -t "Composite/Sod/PseudoUG/2d/AMReX/simpleUnsplit" -np 4 -cbase 2023-01-13 -rbase 2023-01-14
    \b
        Sod -t "Comparison/Sod/UG/2d/simpleUnsplit" -np 1 -e OMP_NUM_THREADS=1 -e OMP_STACKSIZE=16M -cbase 2023-01-13

    \b
    The first value represents a Flash-X setup defined in
    source/Simulation/SimulationMain directory with following
    options,

    \b
    -t, --test		TEXT	Defined in */tests/tests.yaml
    -np, --nprocs	TEXT	Number of processors
    -cbase, --cbase	TEXT	Date for comparsion benchmark
    -rbase, --rbase	TEXT	Date for restart benchmark
    -tol, --tolerance	FLOAT	Tolerance for comparsion and composite tests
    -e, --env		TEXT	Environment variables
    --debug		BOOLEAN	Debug test
    """
    api.setup_suite(pathToSuites=suitelist)


@flashxtest.command(name="run-suite")
@click.option("--archive", is_flag=True, help="Save results to main archive")
def run_suite(archive):
    """
    \b
    Run the test suite using "test.info".

    \b
    This command runs all the tests defined in
    "test.info", and conveys errors
    """
    api.run_suite(saveToMainArchive=archive)


@flashxtest.command(name="check-suite")
@click.argument("suitelist", type=str, nargs=-1)
def check_suite(suitelist):
    """
    \b
    Check and report changes to "test.info".

    \b
    This command will compare "test.info"
    with "suite" files and report if changes
    are detected
    """
    api.check_suite(pathToSuites=suitelist)


@flashxtest.command(name="show")
@click.argument("setupname", type=str, required=True)
def show(setupname):
    """
    \b
    Show available tests for a given setup name

    \b
    This command prints tests located in tests/test.yaml
    for a given simulation name.
    """
    api.show_tests(setupName=setupname)


@flashxtest.command(name="compile")
@click.argument("setupname", type=str, required=True)
@click.option("--test", "-t", type=str, required=True)
@click.option("-objdir", type=str, default="object")
def compile(setupname, test, objdir):
    """
    \b
    Compile a test defined for a specific setup

    \b
    This command compiles a test defined
    in tests.yaml for a specific setup
    """
    api.dry_run(
        setupName=setupname,
        nodeName=test,
        objDir=os.path.join(os.getcwd(), objdir),
        run_test=False,
    )


@flashxtest.command(name="run")
@click.argument("setupname", type=str, required=True)
@click.option("--test", "-t", type=str, required=True)
@click.option("--nprocs", "-np", type=str, required=True)
@click.option("-objdir", type=str, default="object")
def run(setupname, test, nprocs, objdir):
    """
    \b
    Compile and run a test defined for a specific setup

    \b
    This command compiles and runs a test defined
    in tests.yaml for a specific setup
    """
    api.dry_run(
        setupName=setupname,
        nodeName=test,
        numProcs=nprocs,
        objDir=os.path.join(os.getcwd(), objdir),
        run_test=True,
    )
