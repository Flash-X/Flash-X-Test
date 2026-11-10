"""Python API for FlashXTest"""

import os
from pathlib import Path
from .. import lib
from .. import backend
from ._setupSuite import setup_suite


def run_suite(
    saveToArchive=False,
    skipViewArchive=False,
    skipMainArchive=False,
    pathToSuites=(),
    setup=False,
    addSetupOptions=None,
    webviewDir=None,
    webviewLabel=None,
):
    """
    Run a list of tests from test.info in current working directory

    Arguments
    ---------
    saveToArchive	: True/False
    skipViewArchive	: True/False
    skipMainArchive	: True/False
    pathToSuites	: List of suite files used if test.info has to be created
    setup		: True to regenerate test.info from suite files even if present
    addSetupOptions	: Additional setup options used if test.info is created
    webviewDir		: If set, publish results to the website in this directory
    webviewLabel	: Label for the published results (e.g. main, staged)

    If test.info is not present in the working directory (or setup is True),
    it is created from the suite files first, as "setup-suite" would.
    """
    # Create test.info if needed before anything else
    if setup or not os.path.exists(os.path.join(os.getcwd(), "test.info")):
        setup_suite(
            pathToSuites=pathToSuites,
            overwriteCurrInfo=True,
            addSetupOptions=addSetupOptions,
        )

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

    # Run flashTest - actually call the backend flashTest.py here. Results
    # are published even if the run reports failures, since failures are
    # exactly what the webview should show.
    try:
        lib.run.flashTest(mainDict)
    finally:
        if webviewDir:
            backend.Webview.publish_results(
                Path(webviewDir), webviewLabel, Path(mainDict["pathToOutdir"])
            )
