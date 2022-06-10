"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import toml

from .. import backend


def parseTest(simDir, testKey, mainDict):
    """
    Arguments:
    ----------
    simDir    : Simulation directory
    testKey   : Key for test
    mainDict  : Main dictionary
    """
    # Get path to simulation directory
    pathToSim = mainDict["pathToFlash"] + "/source/Simulation/SimulationMain/" + simDir

    # Read the test info from toml file
    infoDict = toml.load(pathToSim + "/" + "test.toml")[testKey]

    infoDict["setupName"] = simDir

    return infoDict


def checkTest(infoDict, mainDict):
    """
    Arguments:
    ----------
    infoDict  :
    mainDict  : Main dictionary
    """
    # mainNode
    mainNode = backend.xmlNode.parseXml(mainDict["testDir"] + "/" + "testInfo.xml")

    # get node list from test
    nodeList = infoDict["testNode"].split("/")

    # find test nodes
    testNode = mainNode.findChild(nodeList[0])

    for node in nodeList[1:]:
        if testNode:
            testNode = testNode.findChild(node)

    return testNode


def addTest(infoDict, mainDict):
    """
    Arguments:
    ----------
    infoDict :
    mainDict : Main dictionary
    """
    # Create testDir/.fxt if it does not exists
    # TODO: This is probably not needed since 'testDir/.fxt' is already
    # create during getMainDict
    subprocess.run(
        "mkdir -pv {0}".format(str(mainDict["testDir"]) + "/.fxt"), shell=True
    )

    # Create temporary file
    pathToInfo = str(mainDict["testDir"]) + "/.fxt" + "/test.info"

    # infoFile
    infoFile = open("{0}".format(pathToInfo), "w")

    # Parse mainNode
    mainNode = backend.lib.xmlNode.parseXml(str(mainDict["testDir"]) + "/testInfo.xml")

    # get node list from infoDict
    nodeList = infoDict["testNode"].split("/")

    for testType in ["UnitTest", "Composite", "Comparison"]:

        allTests = mainNode.findChild(testType)

        if allTests:
            # Create an entry for testType in pathToInfo
            infoFile.write("<{0}>\n".format(testType))

            for line in allTests.getXml()[1:-1]:
                infoFile.write("{0}\n".format(line))

            if nodeList[0] == testType:

                indent = 2
                for newNode in nodeList[1:]:
                    infoFile.write(indent * " " + "<{0}>\n".format(newNode))
                    indent = indent + 2

                infoFile.write(
                    indent * " " + "setupName: " + infoDict["setupName"] + "\n"
                )
                infoFile.write(
                    indent * " " + "setupOptions: " + infoDict["setupOptions"] + "\n"
                )
                infoFile.write(
                    indent * " " + "numProcs: " + str(infoDict["numProcs"]) + "\n"
                )
                infoFile.write(
                    indent * " "
                    + "parfiles: <pathToSimulations>"
                    + "/"
                    + infoDict["setupName"]
                    + "/"
                    + infoDict["parFile"]
                    + "\n"
                )

                indent = indent - 2
                for newNode in reversed(nodeList[1:]):
                    infoFile.write(indent * " " + "</{0}>\n".format(newNode))
                    indent = indent - 2

            # Close the entry for testType in pathToInfo
            infoFile.write("</{0}>\n".format(testType))

    subprocess.run(
        "mv {0} {1}".format(pathToInfo, mainDict["testDir"] + "/testInfo.xml"),
        shell=True,
    )
