"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend


def run(**apiDict):
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

    # Environment variable for OpenMP
    # Set the default value. Each test
    # can override this from xml file
    os.environ["OMP_NUM_THREADS"] = str(1)

    # Get mainDict
    mainDict = lib.config.getMainDict(apiDict)

    # Parse test.info and create a testList
    jobList = []
    lib.info.jobListFromNode(
        backend.FlashTest.lib.xmlNode.parseXml(apiDict["pathToInfo"]), jobList
    )

    # Build sfocu for performing checks with baseline data
    # for Composite and Comparison tests
    lib.run.buildSFOCU(mainDict)

    # Run flashTest - actually call the backend flashTest.py here
    lib.run.flashTest(mainDict, jobList)
