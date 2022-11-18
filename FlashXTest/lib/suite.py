"""FlashXTest library to interface with backend.FlashTest"""

import os, subprocess
import itertools
import glob
import argparse
import shlex

from .. import backend
from .. import lib


class TestSpec:
    """
    Class TestSpec to handle test specifications
    """

    def __init__(self):
        """
        Constructor
        """
        for attr in [
            "setupName",
            "nodeName",
            "setupOptions",
            "numProcs",
            "parfiles",
            "restartParfiles",
            "transfers",
            "environment",
            "debug",
        ]:
            setattr(self, attr, None)

    def getXmlText(self):
        """
        get Xml text from test specifications
        """

        # Create an empty list
        xmlText = []

        # Deal with parfile paths
        if self.parfiles:
            if self.parfiles == "<defaultParfiles>":
                pass
            else:
                parFileList = self.parfiles.split(" ")
                parFileList = [
                    "<pathToSimulations>" + "/" + self.setupName + "/tests/" + parfile
                    for parfile in parFileList
                ]
                self.parfiles = " ".join(parFileList)

        else:
            raise ValueError(
                lib.colors.FAIL
                + f"'parfiles' not defined for test {self.nodeName!r} for setup {self.setupName!r}"
            )

        # Deal with debug flags
        if self.debug:
            self.setupOptions = self.setupOptions + " -debug"

        # Deal with restartParfiles path
        if self.restartParfiles:
            parFileList = self.restartParfiles.split(" ")
            parFileList = [
                "<pathToSimulations>" + "/" + self.setupName + "/tests/" + parfile
                for parfile in parFileList
            ]
            self.restartParfiles = " ".join(parFileList)

        # Deal with environment variables
        if self.environment:
            self.environment = " ".join(
                list(itertools.chain.from_iterable(self.environment))
            )

        # append to xmlText
        for xmlKey in list(self.__dict__.keys()):
            if getattr(self, xmlKey):
                xmlText.append(f"{xmlKey}: {getattr(self, xmlKey)}")

        return xmlText


def __continuationLines(fin):
    for line in fin:
        line = line.rstrip("\n")
        while line.endswith("\\"):
            line = line[:-1] + next(fin).rstrip("\n")
        yield line


def parseSuite(mainDict):
    """
    Arguments
    ---------
    mainDict : Dicitionary for the API

    Returns
    specList : List of test specifications
    """
    # Set an empty dictionary to populate
    specList = []

    # Check if pathToSuites is defined, if not use
    # all *.suite files from the working directory
    if not mainDict["pathToSuites"]:
        mainDict["pathToSuites"] = glob.glob("*.suite")

    # Create a test suite parser
    suiteParser = argparse.ArgumentParser(description="Parser for test suite")
    suiteParser.add_argument("-t", "--test", help="Test node", type=str)
    suiteParser.add_argument("-np", "--nprocs", help="Num procs", type=int)
    suiteParser.add_argument(
        "-e", "--env", action="append", nargs="+", help="Environment variable", type=str
    )
    suiteParser.add_argument("--debug", action="store_true")
    suiteParser.set_defaults(debug=False, nprocs=1, test="", env=None)

    # Loop over all suite files and populate
    # suite dictionary
    for suiteFile in mainDict["pathToSuites"]:

        # Handle exceptions
        if not suiteFile.endswith(".suite"):
            raise ValueError(
                lib.colors.FAIL
                + f'[FlashXTest] File {suiteFile} must have a ".suite" suffix'
            )

        if not os.path.exists(suiteFile):
            raise ValueError(lib.colors.FAIL + f"[FlashXTest] Cannot find {suiteFile}")

        suiteList = []

        with open(suiteFile, "r") as sfile:
            for line in __continuationLines(sfile):
                suiteList.append(line.split("#")[0])

        suiteList = [spec for spec in suiteList if spec]

        for spec in suiteList:

            testSpec = TestSpec()
            testSpec.setupName = shlex.split(spec)[0]

            testArgs = suiteParser.parse_args(shlex.split(spec)[1:])
            testSpec.nodeName = testArgs.test

            for currSpec in specList:
                if testSpec.nodeName in currSpec.nodeName:
                    raise ValueError(
                        lib.colors.FAIL
                        + f"[FlashXTest] Duplicate for {testSpec.nodeName!r} detected in suite files"
                    )

            testSpec.numProcs = testArgs.nprocs
            testSpec.environment = testArgs.env
            testSpec.debug = testArgs.debug

            specList.append(testSpec)

    return specList
