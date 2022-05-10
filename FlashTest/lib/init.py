"""FlashXTest library to interface with backend.FlashTest"""

import os, subprocess

from .. import backend


def setConfig(apiDict):
    """
    Setup configuration

    Arguments
    ---------
    apiDict    : API dictionary
    """
    # Get path to configuration template from FlashTest backend
    configTemplate = os.path.dirname(backend.__file__) + "/FlashTest/configTemplate"

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
    configMain = str(apiDict["testDir"]) + "/.fxt" + "/config"
    configBase = os.path.dirname(backend.__file__) + "/FlashTest/configBase"

    # Create .fxt folder to write configMain
    subprocess.run(
        "mkdir -pv {0}".format(str(apiDict["testDir"]) + "/.fxt"), shell=True
    )

    # Build configMain from configApi and configBase
    subprocess.run(
        "cat {0} {1} > {2}".format(configApi, configBase, configMain), shell=True
    )

    # Parse the configMain file
    mainDict = backend.flashTestParser.parseFile(configMain)

    # Update mainDict with values from apiDict
    for key, value in apiDict.items():
        if value and key in mainDict:
            mainDict[key] = value

    # Set pathToConfig for mainDict
    mainDict["pathToConfig"] = configMain

    # Set testDir
    mainDict["testDir"] = apiDict["testDir"]

    return mainDict


def setInfo(mainDict):
    """
    Get test info site

    Arguments:
    -----------
    mainDict : Main dictionary

    Return:
    -------
    pathToInfo : Site xml file
    """
    # Create testDir/.fxt if it does not exists
    # TODO: This is probably not needed since 'testDir/.fxt' is already
    #       during getMainDict
    subprocess.run(
        "mkdir -pv {0}".format(str(mainDict["testDir"]) + "/.fxt"), shell=True
    )

    # ---------------------------------------------------------------------------------------------
    # Set variables for site Info
    pathToInfo = str(mainDict["testDir"]) + "/.fxt" + "/test.info"

    # Build pathToInfo
    # This done to 'trick' backend/FlashTest/flashTest.py
    # TODO: Find an elegant way to do this
    infoFile = open("{0}".format(pathToInfo), "w")

    # Create a node for site
    infoFile.write("<{0}>\n".format(mainDict["flashSite"]))

    # Iterate over a list of nodeName, find corresponding
    # entry for each in testName.xml and append it to
    # pathToInfo
    for nodeName in ["UnitTest", "Composite", "Comparison"]:

        # Create an entry for nodeName in pathToInfo
        infoFile.write("<{0}>\n".format(nodeName))

        # Parse xml file for each test, extract data, and append it to
        # test.info
        InfoNode = backend.lib.xmlNode.parseXml(
            str(mainDict["testDir"]) + "/testInfo.xml"
        )
        InfoChild = InfoNode.findChild(nodeName)

        if InfoChild:
            for line in InfoChild.getXml()[1:-1]:
                infoFile.write("{0}\n".format(line))

        # Close the entry for nodeName in pathToInfo
        infoFile.write("</{0}>\n".format(nodeName))

    # Close the node for site
    infoFile.write("</{0}>\n".format(mainDict["flashSite"]))

    infoFile.close()

    mainDict["pathToInfo"] = pathToInfo
