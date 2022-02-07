"""Python API for FlashXTest"""

import os
from .. import lib

def run(testDict,shallow=False,**apiDict):
    """
    Run a list of tests from xml file 

    Arguments
    ---------
    testDict : {testName : testList}
             
                 testName : Name of the test xml file
                 testList : Tests to run from xml file

    shallow  : Flag (True/False) 

    apiDict  : Dictionary to override values from Config file
    """
    # Cache the value to current directory and set it as 
    # testDir in apiDict
    apiDict['testDir'] = os.getcwd()

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict['pathToConfig'] =  apiDict['testDir']+'/Config'

    # Environment variable for OpenMP
    # Set the default value. Each test
    # can override this from xml file
    os.environ['OMP_NUM_THREADS'] = str(1)

    # Get mainDict for performing tests. This will read
    # the user Config file and set values that
    # were not provided in apiDict and override values
    # that were
    mainDict = lib.init.getMainDict(apiDict)

    # Build a 'test.info' file from all
    # testName.xml files in testDict, and 
    # Set pathToInfo in mainDict 
    lib.init.setPathToInfo(testDict,mainDict)

    # Run shallow or deep based on flag
    if shallow:
        __shallowRun(testDict,mainDict)
    else:
        __deepRun(testDict,mainDict)

def __shallowRun(testDict,mainDict):
    """
    testDict: Test dictionary
    mainDict: Main dictionary
    """
    pass

def __deepRun(testDict,mainDict):
    """
    testDict: Test dictionary
    mainDict: Main dictonary
    """
    # Build sfocu for performing checks with baseline data
    # for Composite and Comparison tests
    lib.run.buildSFOCU(mainDict)

    # Run flashTest - actually call the backend flashTest.py here
    lib.run.flashTest(testDict,mainDict)
