"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess

from .. import backend
from .. import lib


def flashTest(mainDict, jobList):
    """
    Run flashTest.py from backend/FlashTest

    Arguments:
    ----------
    Arguments:
    mainDict  : Main dictionary
    jobList   : List of jobs
    """
    # remove site from jobList
    jobList = [job.replace(f'{mainDict["flashSite"]}/', "") for job in jobList]

    # Create output directory for TestResults if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["pathToOutdir"]), shell=True)

    # Create archive directory if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["pathToLocalArchive"]), shell=True)

    # Create baseLine directory if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["baselineDir"]), shell=True)

    optString = __getOptString(mainDict)

    # run backend/FlashTest/flashTest.py with desired configuration
    #
    testProcess = subprocess.run(
        "python3 {0}/FlashTest/flashTest.py \
                                          {1} \
                                          {2}".format(
            os.path.dirname(backend.__file__), optString, " ".join(jobList)
        ),
        shell=True,
    )

    os.environ["EXITSTATUS"] = str(testProcess.returncode)
    os.environ["FLASH_BASE"] = mainDict["pathToFlash"]
    os.environ["RESULTS_DIR"] = (
        mainDict["pathToOutdir"] + os.sep + mainDict["flashSite"]
    )

    # try:
    checkProcess = subprocess.run(
        "bash $FLASHTEST_BASE/error.sh", shell=True, check=True
    )

    print(lib.colors.OKGREEN + "[FlashXTest] SUCCESS")

    # except checkProcess.CalledProcessError as e:
    #    #print(lib.colors.FAIL + f"{e.output}")
    #    print(e.output)


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
