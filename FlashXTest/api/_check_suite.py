"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def check_suite(**apiDict):
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

    # Get mainDict
    mainDict = lib.config.getMainDict(apiDict)

    # Check suite
    lib.suite.checkSuite(
        mainDict, backend.FlashTest.lib.xmlNode.parseXml(apiDict["pathToInfo"])
    )
