"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import warnings
import yaml

from .. import backend
from .. import lib


class TestLoader(yaml.SafeLoader):
    """
    Class TestLoader for YAML
    """

    def __init__(self, stream):
        """
        Constructor
        """
        super().__init__(stream)
        self._stream = stream

    def construct_mapping(self, node, deep=False):
        """
        Mapping function
        """
        mapping = set()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(
                    lib.colors.FAIL
                    + f"[FlashXTest] Duplicate {key!r} key found in {self._stream.name!r}."
                )
            mapping.add(key)
        return super().construct_mapping(node, deep)


def loadYaml(filename):
    """
    Arguments
    ---------
    filename : name of the file to parse

    Returns
    -------
    yamlDict : YAML dictionary
    """
    # Load yaml
    with open(filename, "r") as stream:
        try:
            yamlDict = yaml.load(stream, Loader=TestLoader)

        except yaml.YAMLError as exc:
            print(exc)

    return yamlDict


def parseYaml(mainDict, setupName, testNode):
    """
    Arguments:
    ----------
    mainDict  : Main dictionary
    setupName : Setup name
    testNode  : Key for test
    """
    # Get path to simulation directory
    pathToSim = (
        mainDict["pathToFlash"] + "/source/Simulation/SimulationMain/" + setupName
    )

    infoDict = loadYaml(pathToSim + "/tests/" + "tests.yaml")[testNode]

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
                + f'in {pathToSim + "/tests/" + "tests.yaml"}'
            )

    return infoDict


def getXmlText(infoDict):
    """
    Arguments:
    ----------
    infoDict: Test info dictionary
    """
    # Create an empty list
    xmlText = []

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

    if infoDict["debug"]:
        infoDict["setupOptions"] = infoDict["setupOptions"] + " -debug"

    for xmlKey in [
        "setupName",
        "setupOptions",
        "numProcs",
        "parfiles",
        "restartParfiles",
        "transfers",
        "environment",
    ]:
        if xmlKey in infoDict.keys():
            if infoDict[xmlKey]:
                xmlText.append(f"{xmlKey}: {infoDict[xmlKey]}")

    return xmlText
