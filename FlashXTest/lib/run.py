"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import toml

from .. import backend
from .. import lib


def flashTest(mainDict):
    """
    Run flashTest.py from backend/FlashTest

    Arguments:
    ----------
    Arguments:
    mainDict  : Main dictionary
    """

    # Create output directory for TestResults if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["pathToOutdir"]), shell=True)

    # Create archive directory if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["pathToLocalArchive"]), shell=True)

    # Create baseLine directory if it does not exist
    subprocess.run("mkdir -pv {0}".format(mainDict["pathToMainArchive"]), shell=True)

    optString = __getOptString(mainDict)

    # Parse test.info and create a testList
    jobList = []

    # Update jobList
    lib.info.jobListFromNode(
        backend.FlashTest.lib.xmlNode.parseXml(mainDict["pathToInfo"]),
        jobList,
        createBenchmarks=mainDict["createBenchmarks"],
    )

    # remove site from jobList
    jobList = [job.replace(f'{mainDict["flashSite"]}/', "") for job in jobList]

    # run backend/FlashTest/flashTest.py with desired configuration
    #
    testProcess = subprocess.run(
        "python3 {0}/FlashTest/flashTest.py \
                                          {1} \
                                          {2}".format(
            os.path.dirname(backend.__file__), optString, " ".join(jobList)
        ),
        shell=True,
        check=True,
    )

    os.environ["EXITSTATUS"] = str(testProcess.returncode)
    os.environ["FLASH_BASE"] = mainDict["pathToFlash"]
    os.environ["RESULTS_DIR"] = (
        mainDict["pathToOutdir"] + os.sep + mainDict["flashSite"]
    )

    invocationDict = toml.load(
        mainDict["pathToOutdir"]
        + os.sep
        + mainDict["flashSite"]
        + os.sep
        + "invocation.toml"
    )

    for key, value in invocationDict.items():
        os.environ[key] = value

    if mainDict["createBenchmarks"]:
        print(
            "------------------------------------------------------------------------------------------\n"
            + f"[FlashXTest] Benchmark run complete, verify results in:\n"
            + f'"{mainDict["pathToOutdir"]}/{mainDict["flashSite"]}/{invocationDict["INVOCATION_DIR"]}"\n'
            + f"...Before updating test suite..\n"
            + "------------------------------------------------------------------------------------------"
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
        "pathToExeScript": "-e",
    }

    optString = "-v -L "

    for option in optDict:
        if option in mainDict:
            optString = optString + "{0} {1} ".format(optDict[option], mainDict[option])

    if not mainDict["saveToMainArchive"]:
        optString = optString + "-t "

    return optString
