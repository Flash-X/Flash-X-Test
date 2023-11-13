"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def check_suite(pathToSuites):
    """
    Run a list of tests from test.info in current working directory

    Arguments
    ---------
    pathToSuites : A list of suite files
    """
    apiDict = locals()

    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

    # Logfile
    apiDict["log"] = backend.FlashTest.lib.logfile.Logfile(
        apiDict["testDir"], "flashxtest_api.log", verbose=True
    )

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    # Set path to Info
    apiDict["pathToInfo"] = apiDict["testDir"] + "/test.info"

    # Get mainDict
    mainDict = lib.config.getMainDict(apiDict)

    # Check suite
    lib.suite.checkSuiteWithInfo(
        mainDict, backend.FlashTest.lib.xmlNode.parseXml(apiDict["pathToInfo"])
    )
