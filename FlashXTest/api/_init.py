"""Python API for FlashXTest"""

import os

from .. import lib
from .. import backend


def init(**apiDict):
    """
    Initialize test configuration

    Arguments
    ---------
    apiDict : Dictionary to populate Config file
    """
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()

    if not apiDict["pathToFlash"]:
        apiDict["pathToFlash"] = os.getcwd()

    if not apiDict["pathToLocalArchive"]:
        apiDict["pathToLocalArchive"] = os.getcwd() + "/TestLocalArchive"

    if not apiDict["pathToMainArchive"]:
        apiDict["pathToMainArchive"] = os.getcwd() + "/TestMainArchive"

    if not apiDict["pathToOutdir"]:
        apiDict["pathToOutdir"] = os.getcwd() + "/TestResults"

    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

    # Set Config file
    __setConfig(apiDict)

    # Set exeScript
    __setExeScript(apiDict)


def __setExeScript(apiDict):
    """
    Arguments:
    ---------
    apiDict: Dictionary to populate Config file
    """
    apiDict["pathToExeScript"] = apiDict["testDir"] + "/execfile"

    # Check if pathToExeScript already exists and
    # skip the setup process
    if os.path.exists(apiDict["pathToExeScript"]):
        apiDict["log"].err(
            '"execfile" already exists in working directory'
        )

    # Setup configuration if pathToConfig does not exist
    else:
        lib.config.setExe(apiDict)


def __setConfig(apiDict):
    """
    Arguments:
    ---------
    apiDict: Dictionary to populate Config file
    """
    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    # Check if pathToConfig already exists and
    # skip the setup process
    if os.path.exists(apiDict["pathToConfig"]):
        apiDict["log"].err(
            '"config" already exists in working directory'
        )

    # Setup configuration if pathToConfig does not exist
    else:
        lib.config.setConfig(apiDict)
