"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess

from .. import backend
from .. import lib

sys.tracebacklimit = 1


def __fileToList(filePath):
    """
    Static method to convert a file to a list of lines

    Arguments
    ---------
    filePath: string (name of file - full path)

    Returns
    -------
    fileList: list of lines
    """
    # Create an empty list
    # to populate as the file is passed
    fileList = []

    # Open the input file in read-only mode
    with open(filePath, "r") as workingFile:

        # loop over lines
        # in working file
        for line in workingFile:
            # append to
            # file list
            fileList.append(line.strip())

    return fileList


def checkBenchmarks(mainDict, infoNode, jobList):
    """
    Check and populate TODO

    mainDict : Main Dictonary
    infoNode : FlashTest node object
    jobList  : List of jobs
    """
    invocationDir = f'{mainDict["pathToOutdir"]}/{mainDict["flashSite"]}/{os.getenv("INVOCATION_DIR")}'

    mainDict["log"].warn(f"Verify results in - {invocationDir}")
    mainDict["log"].brk()
    mainDict["log"].note('Suggested changes to "*.suite" files:')

    for nodeName in jobList:
        testType = nodeName.split("/")[0]
        xmlText = infoNode.findChildrenWithPath(nodeName)[0].text
        xmlKeys = [entry.split(":")[0] for entry in xmlText]

        if testType == "Comparison":
            if "shortPathToBenchmark" not in xmlKeys:
                mainDict["log"].note(
                    f'Set "cbase" to "{os.getenv("INVOCATION_DIR")}" for "{nodeName}"'
                )

        elif testType == "Composite":
            if "comparisonBenchmark" not in xmlKeys:
                mainDict["log"].note(
                    f'Set "cbase" to "{os.getenv("INVOCATION_DIR")}" for "{nodeName}"'
                )

    invocationLog = __fileToList(f"{invocationDir}/flash_test.log")

    approvedIndex = []
    for index, entry in enumerate(invocationLog):
        if (
            "Restart transparency confirmed, approving restart benchmark in test xml file."
            in entry
        ):
            approvedIndex.append(index)

    approvedTests = []
    for index in approvedIndex:
        for ind in range(index, -1, -1):
            if "test.info" in invocationLog[ind]:
                approvedTests.append(invocationLog[ind + 2].split(":")[1].replace(" ", ""))
                break

    for nodeName in approvedTests:
        mainDict["log"].note(
            f'Set "rbase" to "{os.getenv("INVOCATION_DIR")}" for "{nodeName}"'
        )


def specListFromNode(infoNode, specList):
    """
    Create a list of node paths by recursively searching
    till the end of the tree

    Arguments
    ---------
    infoNode  : FlashTest node object
    specList  : Empty list for test specifications
    """
    if infoNode.subNodes:
        for subNode in infoNode.subNodes:
            specListFromNode(subNode, specList)
    else:
        xmlDict = {}
        for xmlEntry in infoNode.text:
            key, value = xmlEntry.split(":")
            xmlDict.update({key: value.strip()})

        xmlDict["nodeName"] = infoNode.getPathBelowRoot()

        specList.append(xmlDict)


def jobListFromNode(infoNode, jobList):
    """
    Create a list of node paths by recursively searching
    till the end of the tree

    Arguments
    ---------
    infoNode : FlashTest node object
    jobList  : Empty jobList
    """
    skipNode = False

    if infoNode.subNodes:
        for subNode in infoNode.subNodes:
            jobListFromNode(subNode, jobList)

    else:
        jobList.append(infoNode.getPathBelowRoot())


def addNodeFromPath(infoNode, nodePath):
    """
    infoNode : node object
    nodePath : node path
    """
    nodeList = nodePath.split("/")

    for node in nodeList:
        if not infoNode.findChild(node):
            infoNode.add(node)

        infoNode = infoNode.findChild(node)


def createInfo(mainDict, specList):
    """
    Get test info site

    Arguments:
    -----------
    mainDict : Main dictionary
    specList : List of test specifications
    """
    # Set variables for site Info
    pathToInfo = str(mainDict["testDir"]) + "/test.info"

    if os.path.exists(pathToInfo) and not mainDict["overwriteCurrInfo"]:
        mainDict["log"].warn(f"{pathToInfo!r} already exits. Replace? (Y/n):")
        overwrite = input()
        if overwrite == "y" or overwrite == "Y":
            mainDict["log"].note('OVERWRITING current "test.info"')

        else:
            mainDict["log"].note('SKIPPING "test.info" overwrite')
            return

    elif mainDict["overwriteCurrInfo"]:
        mainDict["log"].note('OVERWRITING current "test.info"')

    # Get uniquie setup names
    setupList = []
    for testSpec in specList:
        setupList.append(testSpec.setupName)
    setupList = [*set(setupList)]

    # Get yaml dictionary
    setupYaml = {}
    for setupName in setupList:
        setupYaml[setupName] = lib.yml.parseYaml(mainDict, setupName)

    # Build test.info file from the test suite
    with open(pathToInfo, "w") as testInfoFile:

        # Create xml node to store info
        infoNode = backend.FlashTest.lib.xmlNode.XmlNode("infoNode")

        # Add the site node
        infoNode.add(f'{mainDict["flashSite"]}')

        # create test node from suiteDict
        for testSpec in specList:

            addNodeFromPath(
                infoNode.findChild(f'{mainDict["flashSite"]}'), testSpec.nodeName
            )

            setupInfo = setupYaml[testSpec.setupName][testSpec.nodeName]

            for key in setupInfo.keys():
                if hasattr(testSpec, key):
                    setattr(testSpec, key, setupInfo[key])
                else:
                    mainDict["log"].err(
                        f"{key!r} defined for test {testSpec.nodeName!r}"
                        + f" in {testSpec.setupName!r} does not exist in TestSpec"
                    )
                    raise ValueError()

            infoNode.findChildrenWithPath(testSpec.nodeName)[
                0
            ].text = testSpec.getXmlText()

        # Write xml to file
        for line in infoNode.getXml():
            testInfoFile.write(f"{line}\n")

    mainDict["pathToInfo"] = pathToInfo

    mainDict["log"].note("test.info is setup")
