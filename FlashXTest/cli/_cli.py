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


@flashxtest.group(name="suite")
def suite():
    """
    \b
    Testsuite management
    """
    pass


@flashxtest.group(name="archive")
def archive():
    """
    \b
    Archive management
    """
    pass
