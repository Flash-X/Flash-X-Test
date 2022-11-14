"""Python CLI for flashxtest"""

import os
import pwd
import click
from .. import api
from .. import cli


@cli.suite.command(name="setup")
@click.argument("suitelist", type=str, nargs=-1)
def setup(suitelist):
    """
    \b
    Create a "test.info" from a list of
    suite files. If no arguments are supplied
    all "*.suite" files are used from the working
    directory
    """
    api.suite.setup(pathToSuites=suitelist)


@cli.suite.command(name="run")
def run():
    """
    \b
    Run the test suite using "test.info" from
    the working directory
    """
    # Arguments
    # ---------
    # testsuite : string for the test suite file
    api.suite.run()
