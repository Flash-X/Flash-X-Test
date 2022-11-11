"""Python CLI for flashxtest"""

import os
import pwd
import click
from .. import api


@click.group(name="flashxtest")
def flashxtest():
    """
    Python CLI for Flash-X Testing Utility
    """
    pass


@flashxtest.command(name="init")
@click.option("--source", "-z", default=None, help="Flash-X source directory")
@click.option("--site", "-s", default=None, help="Flash-X site name")
def init(source, site):
    """
    Initialize test configuration
    """
    # Arguments
    # ---------
    # source: Flash-X source directory
    # site: Flash-X site name
    api.init(flashSite=site, pathToFlash=source)


@flashxtest.command(name="run")
@click.argument("testsuite", type=str)
def run(testsuite):
    """
    Run a list of tests from xml file
    """
    # Arguments
    # ---------
    # testsuite : string for the test suite file
    api.run(pathToSuite=testsuite)
