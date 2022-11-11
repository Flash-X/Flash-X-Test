"""Python API for FlashXTest"""

import os
from .. import lib


def run(**apiDict):
    """
    Run a list of tests from xml file

    Arguments
    ---------
    testSuite : Name of the testSuite file
    """
    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    # Environment variable for OpenMP
    # Set the default value. Each test
    # can override this from xml file
    os.environ["OMP_NUM_THREADS"] = str(1)

    # Get mainDict for performing tests. This will read
    # the user Config file and set values that
    # were not provided in apiDict and override values
    # that were
    mainDict = lib.setup.getMainDict(apiDict)

    # Get testSuiteDict from testSuite file
    suiteDict = lib.setup.getSuiteDict(apiDict)

    # Create a test.info file for flashTest backend
    lib.setup.createTestInfo(mainDict, suiteDict)

    # Build sfocu for performing checks with baseline data
    # for Composite and Comparison tests
    lib.run.buildSFOCU(mainDict)

    # Run flashTest - actually call the backend flashTest.py here
    lib.run.flashTest(mainDict, suiteDict)
