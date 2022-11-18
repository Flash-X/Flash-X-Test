"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def setup_suite(**apiDict):
    """
    Setup test.info from a list of suites

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

    # Get mainDict for performing tests. This will read
    # the user Config file and set values that
    # were not provided in apiDict and override values
    # that were
    mainDict = lib.config.getMainDict(apiDict)

    # Get specList from suite files
    specList = lib.suite.parseSuite(mainDict)

    # Create a test.info file for flashTest backend
    lib.info.createInfo(mainDict, specList)
