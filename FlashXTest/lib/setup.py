"""FlashXTest library to interface with backend.FlashTest"""

import os, subprocess
import argparse
import shlex

from .. import backend
from .. import lib


def setConfig(apiDict):
    """
    Setup configuration

    Arguments
    ---------
    apiDict    : API dictionary
    """
    # Get path to configuration template from FlashTest backend
    configTemplate = os.path.dirname(backend.__file__) + "/FlashTest/configTemplate"

    # Get path to configuration base from FlashTest backend
    configBase = os.path.dirname(backend.__file__) + "/FlashTest/configBase"

    # Get path to user configuration file from apiDict
    configFile = apiDict["pathToConfig"]

    # Start building configFile from configTemplate
    #
    # configTemplate in read mode as ctemplate
    # configFile in write mode as cfile
    #
    with open(configTemplate, "r") as ctemplate, open(configFile, "w") as cfile:

        # Read lines from ctemplate
        lines = ctemplate.readlines()

        # Iterate over lines and set values defined in apiDict
        for line in lines:

            # Set path to Archive
            line = line.replace(
                "pathToLocalArchive:",
                str("pathToLocalArchive: " + apiDict["testDir"] + "/TestArchive"),
            )

            # Set default baseLineDir
            line = line.replace(
                "baselineDir:",
                str("baselineDir:        " + apiDict["testDir"] + "/TestArchive"),
            )

            # Set default pathToOutdir
            line = line.replace(
                "pathToOutdir:",
                str("pathToOutdir:       " + apiDict["testDir"] + "/TestResults"),
            )

            # Set 'pathToFlash' if defined in apiDict
            if "pathToFlash" in apiDict:
                line = line.replace(
                    "pathToFlash:",
                    str("pathToFlash:        " + str(apiDict["pathToFlash"])),
                )

            # Set 'flashSite' if define in apiDict
            if "flashSite" in apiDict:
                line = line.replace(
                    "flashSite:",
                    str("flashSite:          " + str(apiDict["flashSite"])),
                )

            cfile.write(line)

    # Append additional options from configBase
    #
    with open(configBase, "r") as cbase, open(configFile, "a") as cfile:
        cfile.write("\n")
        cfile.write("# Following options are default values that should\n")
        cfile.write("# not be changed for most cases \n")

        lines = cbase.readlines()

        for line in lines:
            cfile.write(line)

    print("Initialized FlashXTest Configuration")


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
    """
    if not os.path.exists(apiDict["pathToSuite"]):
        raise ValueError(f"[FlashXTest] Cannot find {testSuite}")

    suiteList = []

    with open(apiDict["pathToSuite"], "r") as sfile:
        for line in sfile:
            line = line.rstrip("\n")
            suiteList.append(line.split("#")[0])

    suiteList = [spec for spec in suiteList if spec]

    suiteParser = argparse.ArgumentParser(description="Parser for test suite")
    suiteParser.add_argument("-t", "--test", help="Test node", type=str)
    suiteParser.add_argument("-n", "--nprocs", help="Num procs", type=int)
    suiteParser.add_argument("--debug", action="store_true")

    suiteParser.set_defaults(debug=False, nprocs=1, test="")

    suiteDict = {}

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


def createTestInfo(mainDict, suiteDict):
    """
    Get test info site

    Arguments:
    -----------
    mainDict : Main dictionary
    testSuiteDict: Test suite dictionary
    """
    # Set variables for site Info
    pathToInfo = str(mainDict["testDir"]) + "/test.info"

    # Build test.info file from the test suite
    with open(pathToInfo, "w") as infoFile:

        # Create xml node to store info
        infoNode = backend.FlashTest.lib.xmlNode.XmlNode("infoNode")

        # Add the site node
        infoNode.add(f'{mainDict["flashSite"]}')

        # create test node from suiteDict
        for testNode in suiteDict.keys():

            # convert the test node string into a list
            nodeList = testNode.split("/")

            tempNode = infoNode.findChild(f'{mainDict["flashSite"]}')

            for node in nodeList:
                if not tempNode.findChild(node):
                    tempNode.add(node)
                    tempNode = tempNode.findChild(node)

            lib.add.parseTestToml(mainDict, suiteDict, testNode)
            tempNode.text = lib.add.getXmlText(suiteDict, testNode)

        # Write xml to file
        for line in infoNode.getXml():
            infoFile.write(f"{line}\n")

    mainDict["pathToInfo"] = pathToInfo
