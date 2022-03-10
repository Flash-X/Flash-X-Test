"""Python CLI for flashtest"""

import os
import pwd
import click
from .. import api


@click.group(name="flashtest")
def flashtest():
    """
    Python CLI to flashtest
    """
    pass


@flashtest.command(name="init")
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


@flashtest.command(name="run")
@click.option('--site', '-s', default=None, help='Flash-X site name')
@click.option('--outdir', '-o', default=None, help='Output directory')
@click.option('--shallow', is_flag=True, help='Option for shallow run')
@click.argument('joblist', nargs=-1)
def run(joblist,site,outdir,shallow):
    """
    Run a list of tests from xml file
    """
    # Arguments
    # ---------
    # joblist   : List of jobfiles
    # site      : FlashX site name
    # outdir    : Output directory
    # shallow   : Option for shallow run
    api.run(joblist,shallow=shallow,flashSite=site,pathToOutdir=outdir)


@flashtest.command(name="view")
def view():
    """
    Launch webviewer
    """
    pass
