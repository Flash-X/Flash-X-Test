"""Python API for FlashXTest"""

import os
from .. import lib


def init(**apiDict):
    """
    Initialize test configuration

    Arguments
    ---------
    apiDict : Dictionary to populate Config file
    """
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
    apiDict["pathToExeScript"] = apiDict["testDir"] + "/exeScript"
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
        print(
            lib.colors.WARNING
            + "[FlashXTest] Skipping initialization: Config file already exists!"
        )

    # Setup configuration if pathToConfig does not exist
    else:
        lib.config.setConfig(apiDict)
