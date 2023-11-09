"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def remove_benchmarks(**apiDict):
    """
    Remove benchmarks from a list of suites

    Arguments
    ---------
    pathToSuites : List of suite files
    """
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()
    lib.suite.removeBenchmarks(apiDict)


def add_cbase(**apiDict):
    """
    Add -cbase to suite files

    Arguments
    ---------
    pathToSuites : List of suite files
    date : date string
    """
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()
    apiDict["cbaseAdd"] = True
    apiDict["rbaseAdd"] = False
    lib.suite.addBenchmarks(apiDict)


def add_rbase(**apiDict):
    """
    Add -rbase to suite files

    Arguments
    ---------
    pathToSuites : List of suite files
    date : date string
    """
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()
    apiDict["cbaseAdd"] = False
    apiDict["rbaseAdd"] = True
    lib.suite.addBenchmarks(apiDict)
