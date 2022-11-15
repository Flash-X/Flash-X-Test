"""Python CLI for flashxtest"""

import os
import pwd
import click
from .. import api


@click.group(name="flashxtest")
def flashxtest():
    """
    \b
    Command line interface for managing
    Flash-X testing framework
    """
    pass


@flashxtest.command(name="init")
@click.option("--source", "-z", default=None, help="Flash-X source directory")
@click.option("--site", "-s", default=None, help="Flash-X site name")
def init(source, site):
    """
    \b
    Initialize site specific configuration.
    This command create a "config" and "execScript"
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
    If no arguments are supplied
    all "*.suite" files are used from the working
    directory
    """
    api.setup_suite(pathToSuites=suitelist)


@flashxtest.command(name="run")
def run():
    """
    \b
    Run the test suite using "test.info" from
    the working directory
    """
    # Arguments
    # ---------
    # testsuite : string for the test suite file
    api.run()
