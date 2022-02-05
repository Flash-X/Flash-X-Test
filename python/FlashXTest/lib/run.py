"""FlashXTest library to interface with backend.FlashTest"""

import os, sys, subprocess

from .. import backend

def flashTest(mainDict,testName,testList):
    """
    Run flashTest.py from backend/FlashTest

    Arguments:
    ----------
    Arguments:
    mainDict  : Main dictionary
    testName  : Name of test
    testList  : List of tests
    """
    # Cache value of output directory before running
    # individual tests
    pathToOutdir = mainDict['pathToOutdir']

    # Set pathToOutdir for individual test
    mainDict['pathToOutdir'] = pathToOutdir+'/'+str(testName)

    # Create output directory for TestResults
    # if it does not exist
    subprocess.run('mkdir -pv {0}'.format(mainDict['pathToOutdir']),shell=True)

    # Get pathToInfo for the specific test
    #
    __setPathToInfo(mainDict,testName)

    optString = __getOptString(mainDict)

    # run backend/FlashTest/flashTest.py with desired configuration
    #
    testProcess = subprocess.run('python3 {0}/FlashTest/flashTest.py \
                                          {1} \
                                          {2}'.format(os.path.dirname(backend.__file__),
                                                      optString,
                                                      " ".join(testList)), shell=True)

    # Reassign value after running flashTest
    mainDict['pathToOutdir'] = pathToOutdir

    # Handle errors
    # TODO: Add checks to read logs and report error for each test
    # that failed
    if testProcess.returncode != 0:
        print('FlashTest returned exit status {0}'.format(exit_status))
        print('---------------------------------------------------------')
        raise ValueError

    else:
        print('FlashTest reports SUCCESS')

def buildSFOCU(mainDict):
    """
    Build SFOCU (Serial Flash Output Comparison Utility)

    Arguments:
    ----------
    mainDict: Dictionary from Config file
    """
    # Cache value of current directory
    workingDir = os.getenv('PWD')

    # Build brand new version of sfocu
    # cd into sfocu directory and compile a new 
    # version
    os.chdir('{0}/tools/sfocu'.format(mainDict['pathToFlash']))
    subprocess.run('make SITE={0} NO_NCDF=True sfocu clean'.format(mainDict['flashSite']),shell=True)
    subprocess.run('make SITE={0} NO_NCDF=True sfocu'.format(mainDict['flashSite']),shell=True)

    # Append SFOCU path to sys.path
    sys.path.append(os.getenv('PWD'))

    # cd back into workingDir
    os.chdir(workingDir)    

def __getOptString(mainDict):
    """
    Argument
    --------

    mainDict: Dictionary with configuration values
    """
    optDict = { 'pathToFlash'  : '-z',
                'pathToInfo'   : '-i',
                'pathToOutdir' : '-o',
                'pathToConfig' : '-c',
                'flashSite'    : '-s' }

    optString = '-v -L '
    
    for option in optDict:
        if option in mainDict:
            optString = optString + '{0} {1} '.format(optDict[option],mainDict[option])

    return optString

def __setPathToInfo(mainDict,testName):
    """
    Get test info site

    Arguments:
    -----------
    testDir   : Test directory
    testName  : Name of test
    flashSite : Flash-X site

    Return:
    -------
    testSiteInfo : Site xml file
    """
    # Create testDir/.fxt if it does not exists
    # TODO: This is probably not needed since 'testDir/.fxt' is already
    #       during __getMainDict 
    subprocess.run('mkdir -pv {0}'.format(str(mainDict['testDir'])+'/.fxt'),shell=True)

    # Set variables for testInfo and testSiteInfo
    testInfo = str(mainDict['testDir'])+'/{0}.xml'.format(testName)
    testSiteInfo = str(mainDict['testDir'])+'/.fxt'+'/test.info'.format(testName)

    # Build testSiteInfo from testInfo 
    # This done to 'trick' backend/FlashTest/flashTest.py
    # TODO: Find an elegant way to do this
    with open('{0}'.format(testSiteInfo), 'w') as testFile:
        testFile.write('<{0}>\n'.format(mainDict['flashSite']))

    os.system('cat {0} >> {1}'.format(testInfo,testSiteInfo))

    with open('{0}'.format(testSiteInfo), 'a') as testFile:
        testFile.write('</{0}>\n'.format(mainDict['flashSite']))

    mainDict['pathToInfo'] = testSiteInfo
