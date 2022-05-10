"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess

from .. import backend


def flashTest(jobList, mainDict):
    """
    Run flashTest.py from backend/FlashTest

    Arguments:
    ----------
    Arguments:
    jobList   : List of jobs
    mainDict  : Main dictionary
    """
    # Create output directory for TestResults if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["pathToOutdir"]), shell=True)

    # Create archive directory if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["pathToLocalArchive"]), shell=True)

    # Create baseLine directory if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["baselineDir"]), shell=True)

    optString = __getOptString(mainDict)

    # Generate a list of tests from testDict
    testList = []

    for jobInfo in jobList:
        testList.extend(backend.lib.flashTestParser.fileToList(jobInfo))

    # run backend/FlashTest/flashTest.py with desired configuration
    #
    testProcess = subprocess.run(
        "python3 {0}/FlashTest/flashTest.py \
                                          {1} \
                                          {2}".format(
            os.path.dirname(backend.__file__), optString, " ".join(testList)
        ),
        shell=True,
    )

    # Handle errors
    # TODO: Add checks to read logs and report error for each test
    # that failed
    if testProcess.returncode != 0:
        print("FlashTest returned exit status {0}".format(testProcess.returncode))
        print("---------------------------------------------------------")
        raise ValueError

    else:
        print("FlashTest reports SUCCESS")


def buildSFOCU(mainDict):
    """
    Build SFOCU (Serial Flash Output Comparison Utility)

    Arguments:
    ----------
    mainDict: Dictionary from Config file
    """
    # Cache value of current directory
    workingDir = os.getenv("PWD")

    # Build brand new version of sfocu
    # cd into sfocu directory and compile a new
    # version
    os.chdir("{0}/tools/sfocu".format(mainDict["pathToFlash"]))
    subprocess.run(
        "make SITE={0} NO_NCDF=True sfocu clean".format(mainDict["flashSite"]),
        shell=True,
    )
    subprocess.run(
        "make SITE={0} NO_NCDF=True sfocu".format(mainDict["flashSite"]), shell=True
    )

    # Append SFOCU path to PATH
    os.environ["PATH"] += os.path.pathsep + os.getcwd()

    # cd back into workingDir
    os.chdir(workingDir)


def __getOptString(mainDict):
    """
    Argument
    --------

    mainDict: Dictionary with configuration values
    """
    optDict = {
        "pathToFlash": "-z",
        "pathToInfo": "-i",
        "pathToOutdir": "-o",
        "pathToConfig": "-c",
        "flashSite": "-s",
    }

    optString = "-v -L "

    for option in optDict:
        if option in mainDict:
            optString = optString + "{0} {1} ".format(optDict[option], mainDict[option])

    return optString
