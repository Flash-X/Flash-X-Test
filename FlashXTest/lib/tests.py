"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import toml

from .. import backend
from .. import lib


def parseToml(mainDict, suiteDict, testNode):
    """
    Arguments:
    ----------
    mainDict  : Main dictionary
    suiteDict : Suite dictionary
    testNode  : Key for test
    """
    # Get path to simulation directory
    pathToSim = (
        mainDict["pathToFlash"]
        + "/source/Simulation/SimulationMain/"
        + suiteDict[testNode]["setupName"]
    )

    # Read the test info from toml file
    infoDict = toml.load(pathToSim + "/tests/" + "tests.toml")[testNode]

    for key in infoDict.keys():
        if key not in ["setupOptions", "parfiles", "restartParfiles", "transfers"]:
            raise ValueError(
                lib.colors.FAIL
                + f'[FlashXTest] unrecognized key "{key}" for "{testNode}" '
                + f'in {pathToSim + "/tests/" + "tests.toml"}'
            )

    suiteDict[testNode].update(infoDict)


def getXmlText(suiteDict, testNode):
    """
    Arguments:
    ----------
    suiteDict: Suite dictionary
    testNode: testNode
    """
    # Create an empty list
    xmlText = []

    # Set the info dict
    infoDict = suiteDict[testNode]

    xmlText.append(f'setupName: {infoDict["setupName"]}')
    xmlText.append(f'setupOptions: {infoDict["setupOptions"]}')
    xmlText.append(f'numProcs: {infoDict["numProcs"]}')

    if "parfiles" in infoDict.keys():
        parfiles = [
            "<pathToSimulations>" + "/" + infoDict["setupName"] + "/tests/" + parfile
            for parfile in infoDict["parfiles"]
        ]
    else:
        parfiles = ["<defaultParfile>"]

    xmlText.append(f'parfiles: {" ".join(parfiles)}')

    return xmlText
