"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def run_suite(saveToArchive=False, skipViewArchive=False, skipMainArchive=False):
    """
    Run a list of tests from test.info in current working directory

    Arguments
    ---------
    saveToArchive	: True/False
    skipViewArchive	: True/False
    skipMainArchive	: True/False
    """
    apiDict = locals()

    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

    # Logfile
    # apiDict["log"] = backend.FlashTest.lib.logfile.Logfile(
    #    apiDict["testDir"], "flashxtest_api.log", verbose=True
    # )
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    # Set path to Info
    apiDict["pathToInfo"] = apiDict["testDir"] + "/test.info"

    # Set path to exe
    apiDict["pathToExeScript"] = apiDict["testDir"] + "/execfile"

    # Environment variable for OpenMP
    # Set the default value. Each test
    # can override this from xml file
    os.environ["OMP_NUM_THREADS"] = str(1)

    # Get mainDict
    mainDict = lib.config.getMainDict(apiDict)

    # Build sfocu for performing checks with baseline data
    # for Composite and Comparison tests
    lib.run.buildSFOCU(mainDict)

    # Run flashTest - actually call the backend flashTest.py here
    lib.run.flashTest(mainDict)
