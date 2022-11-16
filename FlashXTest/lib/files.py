"""FlashXTest library to interface with backend.FlashTest"""

import os, subprocess
import argparse
import shlex

from .. import backend
from .. import lib


def setExe(apiDict):
    """
    Arguments
    ---------
    apiDict : API dictionary
    """
    pass


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

    print(lib.colors.OKGREEN + "[FlashXTest] Initialized configuration")


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
    with open(pathToInfo, "w") as testInfoFile:

        # Create xml node to store info
        infoNode = backend.FlashTest.lib.xmlNode.XmlNode("infoNode")

        # Add the site node
        infoNode.add(f'{mainDict["flashSite"]}')

        # create test node from suiteDict
        for testNode in suiteDict.keys():

            # convert the test node string into a list
            nodeList = testNode.split("/")

            leafNode = infoNode.findChild(f'{mainDict["flashSite"]}')

            for node in nodeList:

                if not leafNode.findChild(node):
                    leafNode.add(node)

                leafNode = leafNode.findChild(node)

            suiteDict[testNode].update(
                lib.tests.parseYaml(
                    mainDict, suiteDict[testNode]["setupName"], testNode
                )
            )
            leafNode.text = lib.tests.getXmlText(suiteDict[testNode])

        # Write xml to file
        for line in infoNode.getXml():
            testInfoFile.write(f"{line}\n")

    mainDict["pathToInfo"] = pathToInfo
