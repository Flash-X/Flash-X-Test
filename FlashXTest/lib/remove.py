"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import toml

from .. import backend

def removeTest(infoDict, mainDict):
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
        "mkdir -pv {0} && touch {1} && touch {2}".format(
            str(mainDict["testDir"]) + "/.fxt",
            str(mainDict["testDir"]) + "/testInfo.xml",
            str(mainDict["testDir"]) + "/jobFile",
        ),
        shell=True,
    )

    # Create temporary file
    pathToInfo = str(mainDict["testDir"]) + "/.fxt" + "/test.info"

    # infoFile
    infoFile = open("{0}".format(pathToInfo), "w")

    # Parse mainNode
    mainNode = backend.lib.xmlNode.parseXml(str(mainDict["testDir"]) + "/testInfo.xml")

    # get node list from infoDict
    nodeList = infoDict["testNode"].split("/")

    # Remove old test
    for index in range(len(nodeList) - 1, 1, -1):
        oldTest = mainNode.findChild("/".join(nodeList[:index]))
        oldTest.remove(True)

    for testType in ["UnitTest", "Composite", "Comparison"]:

        currTests = mainNode.findChild(testType)

        if currTests:
            # Create an entry for testType in pathToInfo
            infoFile.write("<{0}>\n".format(testType))

        if currTests:
            for line in currTests.getXml()[1:-1]:
                infoFile.write("{0}\n".format(line))

        if currTests:
            # Close the entry for testType in pathToInfo
            infoFile.write("</{0}>\n".format(testType))

    subprocess.run(
        "mv {0} {1}".format(pathToInfo, mainDict["testDir"] + "/testInfo.xml"),
        shell=True,
    )

    jobList = open(mainDict["testDir"] + "/jobFile", "r").readlines()

    if infoDict["testNode"] + "\n" in jobList: jobList.remove(infoDict["testNode"] + "\n")

    with open(mainDict["testDir"] + "/jobFile", "w") as jobFile:
        jobFile.writelines(jobList)
