"""FlashXTest library to interface with backend.FlashTest"""

import os, subprocess
import glob
import argparse
import shlex

from .. import backend
from .. import lib


def getMainDict(apiDict):
    """
    Arguments
    --------
    apiDict  : Dictionary to override values from Config file

    Returns
    -------
    mainDict: Dictionary for keys in the config file
    """
    # Build Config file for mainDict.
    # Read the user Config file (configApi), append it to Base Config from backend (configBase),
    # and create a new Config (configMain) in 'testDir/.fxt' folder
    configApi = apiDict["pathToConfig"]
    configMain = configApi

    # Parse the configMain file
    mainDict = backend.flashTestParser.parseFile(configMain)

    # Update mainDict with values from apiDict
    for key, value in apiDict.items():
        if value and key in mainDict:
            mainDict[key] = value

    # Set pathToConfig for mainDict
    mainDict["pathToConfig"] = apiDict["pathToConfig"]

    # Set testDir
    mainDict["testDir"] = apiDict["testDir"]

    return mainDict


def getSuiteDict(apiDict):
    """
    Arguments
    ---------
    apiDict : Dicitionary for the API

    Returns
    suiteDict : Dictionary for test suite
    """
    # Set an empty dictionary to populate
    suiteDict = {}

    # Check if pathToSuites is defined, if not use
    # all *.suite files from the working directory
    if not apiDict["pathToSuites"]:
        apiDict["pathToSuites"] = glob.glob("*.suite")

    # Create a test suite parser
    suiteParser = argparse.ArgumentParser(description="Parser for test suite")
    suiteParser.add_argument("-t", "--test", help="Test node", type=str)
    suiteParser.add_argument("-n", "--nprocs", help="Num procs", type=int)
    suiteParser.add_argument("--debug", action="store_true")
    suiteParser.set_defaults(debug=False, nprocs=1, test="")

    # Loop over all suite files and populate
    # suite dictionary
    for suiteFile in apiDict["pathToSuites"]:

        # Handle exceptions
        if not suiteFile.endswith(".suite"):
            raise ValueError(
                lib.colors.FAIL
                + f'[FlashXTest] File {suiteFile} must have a ".suite" suffix'
            )

        if not os.path.exists(suiteFile):
            raise ValueError(lib.colors.FAIL + f"[FlashXTest] Cannot find {suiteFile}")

        suiteList = []

        with open(suiteFile, "r") as sfile:
            for line in sfile:
                line = line.rstrip("\n")
                suiteList.append(line.split("#")[0])

        suiteList = [spec for spec in suiteList if spec]

        for spec in suiteList:
            testName = shlex.split(spec)[0]
            testArgs = suiteParser.parse_args(shlex.split(spec)[1:])
            testNode = testArgs.test

            tempDict = {
                testNode: {
                    "setupName": testName,
                    "numProcs": testArgs.nprocs,
                    "debug": testArgs.debug,
                }
            }

            if testNode in suiteDict.keys():
                raise ValueError(
                    f"[FlashXTest] Duplicate for {testNode} detected in testSuite"
                )
            else:
                suiteDict.update(tempDict)

    return suiteDict
