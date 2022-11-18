"""FlashXTest library to interface with backend.FlashTest"""

import os, subprocess

from .. import backend
from .. import lib


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

    if os.path.exists(pathToInfo):
        overwrite = input(
            lib.colors.WARNING
            + f"[FlashXTest] {pathToInfo!r} already exits. Replace? (Y/n) "
        )

        if overwrite == "y" or overwrite == "Y":
            print(lib.colors.OKGREEN + "OVERWRITING")
        else:
            print(lib.colors.OKGREEN + "SKIPPING")
            return

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
                    raise ValueError(
                        f"{key!r} defined for test {testSpec.nodeName!r}"
                        + f" in {testSpec.setupName!r} does exist in TestSpec"
                    )

            infoNode.findChildrenWithPath(testSpec.nodeName)[
                0
            ].text = testSpec.getXmlText()

        # Write xml to file
        for line in infoNode.getXml():
            testInfoFile.write(f"{line}\n")

    mainDict["pathToInfo"] = pathToInfo

    print(lib.colors.OKGREEN + "[FlashXText] test.info is setup")
