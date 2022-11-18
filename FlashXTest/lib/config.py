"""FlashXTest library to interface with backend.FlashTest"""

import os, subprocess

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
    mainDict.update(apiDict)

    return mainDict


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
