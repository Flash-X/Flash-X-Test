"""Python API for FlashXTest"""

import os
from . import lib

def setup(**apiDict):
    """
    Setup test configuration

    Arguments
    ---------
    apiDict : Dictionary to override values from Config file
    """
    # Cache the value to current directory and set it as 
    # testDir in apiDict
    apiDict['testDir'] = os.getenv('PWD')

    # Cache the value of user Config file and store it as
    # configFile in apiDict
    apiDict['configFile'] =  apiDict['testDir']+'/Config'

    # Check if configFile already exists and
    # skip the setup process
    if os.path.exists(apiDict['configFile']):
       print('Skipping setup: Config file already exists!')

    # Setup configuration if configFile does not exist
    else:
        lib.setup(apiDict)

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
    # configFile in apiDict
    apiDict['configFile'] =  apiDict['testDir']+'/Config'

    # Run tests
    lib.run(apiDict,testDict)
