"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def remove_benchmarks(pathToSuites, cbaseDate=None, rbaseDate=None):
    """
    Remove benchmarks from a list of suites

    Arguments
    ---------
    pathToSuites	: List of suite files
    cbaseDate		: Date of comparison benchmark
    rbaseDate		: Date of composite benchmarks
    """
    apiDict = locals()
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()
    lib.suite.removeBenchmarks(apiDict)


def add_cbase(pathToSuites, cbaseDate):
    """
    Add -cbase to suite files

    Arguments
    ---------
    pathToSuites	: List of suite files
    cbaseDate		: Date string
    """
    apiDict = locals()
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()
    apiDict["cbaseAdd"] = True
    apiDict["rbaseAdd"] = False
    lib.suite.addBenchmarks(apiDict)


def add_rbase(pathToSuites, rbaseDate):
    """
    Add -rbase to suite files

    Arguments
    ---------
    pathToSuites	: List of suite files
    rbaseDate		: Date string
    """
    apiDict = locals()
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()
    apiDict["cbaseAdd"] = False
    apiDict["rbaseAdd"] = True
    lib.suite.addBenchmarks(apiDict)
