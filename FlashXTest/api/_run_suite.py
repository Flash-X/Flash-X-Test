"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def run_suite(**apiDict):
    """
    Run a list of tests from test.info in current working directory
    """
    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

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
