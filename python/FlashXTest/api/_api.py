"""Python API for FlashXTest"""

import os
from .. import lib

def init(**apiDict):
    """
    Initialize test configuration

    Arguments
    ---------
    apiDict : Dictionary to populate Config file
    """
    # Cache the value to current directory and set it as 
    # testDir in apiDict
    apiDict['testDir'] = os.getenv('PWD')

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict['pathToConfig'] =  apiDict['testDir']+'/Config'

    # Check if pathToConfig already exists and
    # skip the setup process
    if os.path.exists(apiDict['pathToConfig']):
       print('Skipping initialization: Config file already exists!')

    # Setup configuration if pathToConfig does not exist
    else:
        lib.setConfig(apiDict)

def run(testDict,**apiDict):
    """
    Run a list of tests from xml file 

    Arguments
    ---------
    testDict : {testName : testList}
             
                 testName : Name of the test xml file
                 testList : Tests to run from xml file

    apiDict  : Dictionary to override values from Config file
    """
    # Cache the value to current directory and set it as 
    # testDir in apiDict
    apiDict['testDir'] = os.getenv('PWD')

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
    mainDict = lib.getMainDict(apiDict)

    # Build sfocu for performing checks with baseline data
    # for Composite and Comparison tests
    lib.buildSFOCU(mainDict)

    for testName,testList in testDict.items():
        # Run flashTest - actually call the backend flashTest.py here
        lib.flashTest(mainDict,testName,testList)
