"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import yaml

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

    testDict = {}

    # Read the test info from yaml file
    with open(pathToSim + "/tests/" + "tests.yaml", "r") as stream:
        try:
            testDict.update(yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

    infoDict = testDict[testNode]

    for key in infoDict.keys():
        if key not in [
            "setupOptions",
            "parfiles",
            "restartParfiles",
            "transfers",
        ]:
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

    if "parfiles" not in infoDict.keys():
        infoDict["parfiles"] = "<defaultParfile>"

    elif infoDict["parfiles"] == "<defaultParfile>":
        pass

    else:
        parFileList = infoDict["parfiles"].split(" ")
        parFileList = [
            "<pathToSimulations>" + "/" + infoDict["setupName"] + "/tests/" + parfile
            for parfile in parFileList
        ]
        infoDict["parfiles"] = " ".join(parFileList)

    for xmlKey in [
        "setupName",
        "setupOptions",
        "numProcs",
        "parfiles",
        "restartParfiles",
        "transfers",
    ]:
        if xmlKey in infoDict.keys():
            xmlText.append(f"{xmlKey}: {infoDict[xmlKey]}")

    return xmlText
