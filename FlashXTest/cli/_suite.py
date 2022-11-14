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
    Setup test.info from a list of suites
    """
    api.suite.setup(pathToSuites=suitelist)


@cli.suite.command(name="run")
def run():
    """
    Run the test suite
    """
    # Arguments
    # ---------
    # testsuite : string for the test suite file
    api.suite.run()
