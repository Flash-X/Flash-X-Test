"""Python API for FlashXTest"""

import os
from .. import lib


def remove(testNode, **apiDict):
    """
    Run a list of tests from xml file

    Arguments
    ---------
    simDir:Simulation directory
    testKey:test key from test.toml
    apiDict:Dictionary to override values from Config file
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
    mainDict = lib.init.getMainDict(apiDict)

    apiDict["testNode"] = testNode

    lib.remove.removeTest(apiDict, mainDict)
