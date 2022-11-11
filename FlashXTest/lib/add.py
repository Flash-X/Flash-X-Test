"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import toml

from .. import backend


def parseTestToml(mainDict, suiteDict, testNode):
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

    if "parFiles" in infoDict.keys():
        parfiles = [
            "<pathToSimulations>" + "/" + infoDict["setupName"] + "/tests/" + parfile
            for parfile in infoDict["parFiles"]
        ]
    else:
        parfiles = ["<defaultParfile>"]

    xmlText.append(f'parfiles: {" ".join(parfiles)}')

    return xmlText
