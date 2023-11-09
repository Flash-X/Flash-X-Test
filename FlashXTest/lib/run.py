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
    subprocess.run(
        "mkdir -pv {0}".format(mainDict["pathToOutdir"]), shell=True, check=True
    )

    # Create local archive directory if it does not exist
    subprocess.run(
        "mkdir -pv {0}".format(mainDict["pathToLocalArchive"]), shell=True, check=True
    )

    # Create main archive directory if it does not exist
    if mainDict["pathToMainArchive"]:
        subprocess.run(
            "mkdir -pv {0}".format(mainDict["pathToMainArchive"]),
            shell=True,
            check=True,
        )

    # Create view archive directory if it does not exist
    if (
        mainDict["pathToViewArchive"]
        and mainDict["saveToArchive"]
        and not mainDict["skipViewArchive"]
    ):
        subprocess.run(
            "mkdir -pv {0}".format(
                os.path.join(mainDict["pathToViewArchive"], mainDict["flashSite"])
            ),
            shell=True,
            check=True,
        )

        subprocess.run(
            "cp {0} {1}".format(
                mainDict["pathToInfo"],
                os.path.join(
                    mainDict["pathToViewArchive"], mainDict["flashSite"], "test.info"
                ),
            ),
            shell=True,
            check=True,
        )

        mainDict["pathToInfo"] = os.path.join(
            mainDict["pathToViewArchive"], mainDict["flashSite"], "test.info"
        )

    optString = __getOptString(mainDict)

    # Parse test.info and create a testList
    jobList = []
    infoNode = backend.FlashTest.lib.xmlNode.parseXml(mainDict["pathToInfo"]).findChild(
        mainDict["flashSite"]
    )

    # Update jobList
    lib.info.jobListFromNode(infoNode, jobList)
    jobList = [job.replace(f'{mainDict["flashSite"]}/', "") for job in jobList]

    # Clear the ERROR file bit of a hacky way but should work for the time being
    # with open("{0}/FlashTest/ERROR".format(os.path.dirname(backend.__file__)), "w") as errorFile:
    #    errorFile.write("\n")

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

    # mainDict["log"].brk()

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

    # This removes log file messages for comparison between
    # test.info and suite files
    # lib.info.checkBenchmarks(mainDict, infoNode, jobList)
    # mainDict["log"].brk()

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
    optDict = {
        "pathToInfo": "-i",
        "pathToConfig": "-c",
        "flashSite": "-s",
        "pathToExeScript": "-e",
    }

    optString = "-v -L "

    for option in optDict:
        if option in mainDict:
            optString = optString + "{0} {1} ".format(optDict[option], mainDict[option])

    if not mainDict["saveToArchive"] or mainDict["skipMainArchive"]:
        optString = optString + "-t"

    if (
        mainDict["saveToArchive"]
        and (not mainDict["skipViewArchive"])
        and mainDict["skipMainArchive"]
    ):
        optString = optString + " -vv"

    return optString
