"""Python API for FlashXTest"""

import os
from .. import lib


def add(simDir, testKey, **apiDict):
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

    infoDict = lib.add.parseTest(simDir, testKey, mainDict)

    testExists, nodeExists, queryNode = lib.add.checkTest(infoDict, mainDict)

    if testExists:
        print(f"Test node {infoDict['testNode']} already exists in testInfo.xml")
        overwrite = input("Overwrite existing test? Y/n ")
       
        if overwrite == 'y' or overwrite == 'Y':
            print("OVERWRITING")
            lib.add.addTest(infoDict, mainDict, replaceExisting=True)
        else:
            print("SKIPPING")

    elif nodeExists:
        print(f"Parent node {queryNode} already exists in testInfo.xml. Cannot add test")

    else:
        lib.add.addTest(infoDict, mainDict)
