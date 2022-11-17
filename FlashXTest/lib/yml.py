"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import warnings
import yaml

from .. import backend
from .. import lib


class __YamlLoader(yaml.SafeLoader):
    """
    Class YamlLoader for YAML
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


def parseYaml(mainDict, setupName):
    """
    Arguments:
    ----------
    mainDict  : Main dictionary
    setupName : Setup name
    """
    # Get path to simulation directory
    yamlFile = (
        mainDict["pathToFlash"]
        + "/source/Simulation/SimulationMain/"
        + setupName
        + "/tests/tests.yaml"
    )

    with open(yamlFile, "r") as stream:
        try:
            yamlDict = yaml.load(stream, Loader=__YamlLoader)
        except yaml.YAMLError as exc:
            print(exc)

    for nodeName in yamlDict.keys():
        for key in yamlDict[nodeName].keys():
            if key not in [
                "setupOptions",
                "parfiles",
                "restartParfiles",
                "transfers",
            ]:
                raise ValueError(
                    lib.colors.FAIL
                    + f'[FlashXTest] unrecognized key "{key}" for "{nodeName}" '
                    + f"in {yamlFile}"
                )

    return yamlDict
