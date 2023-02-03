"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess
import toml

from .. import backend
from .. import lib

sys.tracebacklimit = 1


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
    infoNode = backend.FlashTest.lib.xmlNode.parseXml(mainDict["pathToInfo"]).findChild(
        mainDict["flashSite"]
    )

    # Update jobList
    lib.info.jobListFromNode(infoNode, jobList)
    jobList = [job.replace(f'{mainDict["flashSite"]}/', "") for job in jobList]

    # run backend/FlashTest/flashTest.py with desired configuration
    testProcess = subprocess.run(
        "python3 {0}/FlashTest/flashTest.py \
                                          {1} \
                                          {2}".format(
            os.path.dirname(backend.__file__), optString, " ".join(jobList)
        ),
        shell=True,
        check=True,
    )

    mainDict["log"].brk()

    os.environ["EXITSTATUS"] = str(testProcess.returncode)
    os.environ["FLASH_BASE"] = mainDict["pathToFlash"]
    os.environ["FLASHTEST_OUTPUT"] = mainDict["pathToOutdir"]
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

    lib.info.checkBenchmarks(mainDict, infoNode, jobList)

    mainDict["log"].brk()

    # try:
    checkProcess = subprocess.run(
        "bash $FLASHTEST_BASE/error.sh", shell=True, check=True
    )

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
    optDict1 = {
        "pathToFlash": "-z",
        "pathToOutdir": "-o",
        "pathToConfig": "-c",
        "flashSite": "-s",
        "pathToExeScript": "-e",
    }

    optDict2 = {
        "pathToInfo": "-i",
        "pathToViewArchive": "-vv",
    }

    optString = ""

    for option in optDict1:
        if option in mainDict:
            optString = optString + "{0} {1} ".format(optDict1[option], mainDict[option])

    optString = optString + " -v -L "
    
    # if not mainDict["saveToMainArchive"]:
    #     optString = optString + "-t "
        
    for option in optDict2:
        if option in mainDict:
            optString = optString + "{0} {1} ".format(optDict2[option], mainDict[option])

    return optString
