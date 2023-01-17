"""FlashXTest library to interface with backend.FlashTest"""

from datetime import date
import os, subprocess
import itertools
import glob
import argparse
import shlex

from .. import backend
from .. import lib

# Create a test suite parser
SuiteParser = argparse.ArgumentParser(description="Parser for test suite")
SuiteParser.add_argument("-t", "--test", help="Test node", type=str)
SuiteParser.add_argument("-np", "--nprocs", help="Num procs", type=int)
SuiteParser.add_argument(
    "-cbase", "--cbase", help="Date for comparison benchmark", type=str
)
SuiteParser.add_argument(
    "-rbase", "--rbase", help="Date for restart benchmark", type=str
)
SuiteParser.add_argument(
    "-e", "--env", action="append", nargs="+", help="Environment variable", type=str
)
SuiteParser.add_argument("--debug", action="store_true")
SuiteParser.set_defaults(
    debug=False,
    nprocs=1,
    test="",
    env=None,
    cbase=None,
    rbase=None,
)


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
            "checkpointBasename",
            "comparisonNumber",
            "comparisonBenchmark",
            "restartNumber",
            "restartBenchmark",
            "shortPathToBenchmark",
            "debug",
            "cbase",
            "rbase",
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
            if self.parfiles == "<defaultParfile>":
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

        if self.nodeName.split("/")[0] == "Composite":

            self.checkpointBasename = "flashx_hdf5_chk_"
            self.comparisonNumber = "0001"
            self.restartNumber = "0002"

            if self.cbase:
                self.comparisonBenchmark = f"<siteDir>/{self.cbase}/<buildDir>/<runDir>/<checkpointBasename><comparisonNumber>"

            if self.rbase:
                self.restartBenchmark = f"<siteDir>/{self.rbase}/<buildDir>/<runDir>/<checkpointBasename><restartNumber>"

        if self.nodeName.split("/")[0] == "Comparison" and self.cbase:
            self.shortPathToBenchmark = (
                f"<siteDir>/{self.cbase}/<buildDir>/<runDir>/<chkMax>"
            )

        # Deal with environment variables
        if self.environment:
            self.environment = " ".join(
                list(itertools.chain.from_iterable(self.environment))
            )

        # append to xmlText
        for xmlKey in list(self.__dict__.keys()):
            if (getattr(self, xmlKey)) and (xmlKey not in ["cbase", "rbase", "debug"]):
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

            testArgs = SuiteParser.parse_args(shlex.split(spec)[1:])
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
            testSpec.cbase = testArgs.cbase
            testSpec.rbase = testArgs.rbase

            specList.append(testSpec)

    return specList


def checkSuite(mainDict, infoNode):
    """
    Arguments
    ---------
    mainDict : Dicitionary for the API
    """
    infoNode = infoNode.findChild(f'{mainDict["flashSite"]}')

    # Check if pathToSuites is defined, if not use
    # all *.suite files from the working directory
    if not mainDict["pathToSuites"]:
        mainDict["pathToSuites"] = glob.glob("*.suite")

    update_list = []

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

        with open(suiteFile, "r") as sfile:

            # loop over lines
            for line in __continuationLines(sfile):
                if line.split("#")[0]:
                    spec = shlex.split(line.split("#")[0])
                    testArgs = SuiteParser.parse_args(spec[1:])
                    if testArgs.test.split("/")[0] in ["Composite", "Comparison"]:
                        xmlText = infoNode.findChildrenWithPath(testArgs.test)[0].text
                        for entries in xmlText:
                            if entries.split(":")[0] == "restartBenchmark":
                                rbase = [
                                    value
                                    for value in entries.split(":")[1]
                                    .replace(" ", "")
                                    .split("/")
                                    if value
                                    not in [
                                        "<siteDir>",
                                        "<buildDir>",
                                        "<runDir>",
                                        "<checkpointBasename><restartNumber>",
                                    ]
                                ][0]
                                if (not testArgs.rbase) or (testArgs.rbase != rbase):
                                    update_list.append(
                                        f'Update rbase to "{rbase}" for "{testArgs.test}" in "{sfile.name}"'
                                    )

                            elif entries.split(":")[0] == "comparisonBenchmark":
                                cbase = [
                                    value
                                    for value in entries.split(":")[1]
                                    .replace(" ", "")
                                    .split("/")
                                    if value
                                    not in [
                                        "<siteDir>",
                                        "<buildDir>",
                                        "<runDir>",
                                        "<checkpointBasename><comparisonNumber>",
                                    ]
                                ][0]
                                if (not testArgs.cbase) or (testArgs.cbase != cbase):
                                    update_list.append(
                                        f'Update cbase to "{cbase}" for "{testArgs.test}" in "{sfile.name}"'
                                    )

                            elif entries.split(":")[0] == "shortPathToBenchmark":
                                cbase = [
                                    value
                                    for value in entries.split(":")[1]
                                    .replace(" ", "")
                                    .split("/")
                                    if value
                                    not in [
                                        "<siteDir>",
                                        "<buildDir>",
                                        "<runDir>",
                                        "<chkMax>",
                                    ]
                                ][0]
                                if (not testArgs.cbase) or (testArgs.cbase != cbase):
                                    update_list.append(
                                        f'Update cbase to "{cbase}" for "{testArgs.test}" in "{sfile.name}"'
                                    )

    print(lib.colors.WARNING + "[FlashXTest] TODO: ")
    with open(mainDict["testDir"] + os.sep + "TODO.FlashXTest", "w") as update_file:
        for line in update_list:
            print("[FlashXTest] " + line)
            update_file.write(line + "\n")
