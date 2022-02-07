"""Python CLI for FlashXTest"""

import os
import pwd
import click
from .. import api

@click.group(name='FlashXTest')
def FlashXTest():
    """
    Python CLI to FlashXTest
    """
    pass

@FlashXTest.command(name='init')
@click.option('--source', '-z', default=None, help='Flash-X source directory')
@click.option('--site', '-s', default=None, help='Flash-X site name')
def init(source,site):
    """
    Initialize test configuration
    """
    # Arguments
    # ---------
    # source: Flash-X source directory
    # site: Flash-X site name
    api.init(flashSite=site,pathToFlash=source)

@FlashXTest.command(name='run')
@click.option('--name', '-n', required=True, help='Name of test')
@click.option('--site', '-s', default=None, help='Flash-X site name')
@click.option('--outdir', '-o', default=None, help='Output directory')
@click.option('--shallow', is_flag=True, help='Option for shallow run')
@click.argument('testlist', nargs=-1, required=True)
def run(name,site,outdir,shallow,testlist):
    """
    Run a list of tests from xml file
    """
    # Arguments
    # ---------
    # name      : Name of the test sub-directory
    # site      : FlashX site name
    # outdir    : Output directory
    # shallow   : Option for shallow run
    # testlist  : Tests to run from tests.xml file
    api.run({name:testlist},shallow=shallow,flashSite=site,pathToOutdir=outdir)

@FlashXTest.command(name='view')
def view():
    """
    Launch webviewer
    """
    pass 
