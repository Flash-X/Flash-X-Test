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
def init(source, site):
    """
    \b
    Initialize site specific configuration.

    \b
    This command is used to setup site specific
    configuration for your testing environment
    using "config" and "execScript" files. At
    present only "config" file is created since
    this feature is under development.

    \b
    This command will not work if "config" file
    is present in the working directory. To edit
    existing site specific configuration, "config"
    should be edited directly.
    """
    # Arguments
    # ---------
    # source: Flash-X source directory
    # site: Flash-X site name
    api.init(flashSite=site, pathToFlash=source)


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
    The first value represents a Flash-X setup defined in
    source/Simulation/SimulationMain directory with following
    options,

    \b
    -t, --test TEXT	Defined in */tests/tests.yaml)
    -np, --nprocs TEXT	Number of processors
    --debug BOOLEAN	Debug test

    """
    api.setup_suite(pathToSuites=suitelist)


@flashxtest.command(name="run-suite")
def run_suite():
    """
    \b
    Run the test suite using "test.info".

    \b
    This command runs all the tests defined in
    "test.info", and conveys errors
    """
    api.run_suite()


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
    api.dry_run(setupName=setupname, nodeName=test, objDir=objdir, run_test=False)


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
        objDir=objdir,
        run_test=True,
    )
