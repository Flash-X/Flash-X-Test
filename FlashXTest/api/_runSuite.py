"""Python API for FlashXTest"""

import os
from .. import lib
from .. import backend
from ._setupSuite import setup_suite
from ._webview import webview


def run_suite(
    saveToArchive=False,
    skipViewArchive=False,
    skipMainArchive=False,
    pathToSuites=(),
):
    """
    Run a list of tests from test.info in current working directory

    Arguments
    ---------
    saveToArchive	: True/False
    skipViewArchive	: True/False
    skipMainArchive	: True/False
    pathToSuites	: Suite files. If given, test.info is first (re)created
			  from them, as "setup-suite --overwrite" would. If empty,
			  the existing test.info is used.
    """
    if pathToSuites:
        setup_suite(pathToSuites=pathToSuites, overwriteCurrInfo=True)

    apiDict = {
        "saveToArchive": saveToArchive,
        "skipViewArchive": skipViewArchive,
        "skipMainArchive": skipMainArchive,
    }

    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

    # Logfile
    # apiDict["log"] = backend.FlashTest.lib.logfile.Logfile(
    #    apiDict["testDir"], "flashxtest_api.log", verbose=True
    # )
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    # Set path to Info
    apiDict["pathToInfo"] = apiDict["testDir"] + "/test.info"

    # Set path to exe
    apiDict["pathToExeScript"] = apiDict["testDir"] + "/execfile"

    # Environment variable for OpenMP
    # Set the default value. Each test
    # can override this from xml file
    os.environ["OMP_NUM_THREADS"] = str(1)

    # Get mainDict
    mainDict = lib.config.getMainDict(apiDict)

    # Build sfocu for performing checks with baseline data
    # for Composite and Comparison tests
    lib.run.buildSFOCU(mainDict)

    # Run flashTest - actually call the backend flashTest.py here. The
    # webview is rebuilt even if the run reports failures, since failures are
    # exactly what it should show.
    try:
        lib.run.flashTest(mainDict)
    finally:
        if mainDict.get("pathToWebview"):
            try:
                webview(outdir=mainDict["pathToWebview"])
            except Exception as err:
                # Do not hide the result of the run itself
                apiDict["log"].warn(f"Webview not generated: {err}")
