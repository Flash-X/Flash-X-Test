"""FlashXTest library to interface with backend.FlashTest"""

import os,subprocess

from ... import backend

def run(apiDict,testDict):
    """
    Run list of tests from xml file

    Arguments:
    ----------
    Arguments:
    apiDict   : API dictionary
    testDict  : Test dictionary
    """
    # Environment variable for OpenMP
    # Set the default value. Each test
    # can override this from xml file
    os.environ['OMP_NUM_THREADS'] = str(1)

    # Get mainDict for performing tests. This will read
    # the user Config file and set values that
    # were not provided in apiDict and override values
    # that were
    mainDict = __getMainDict(apiDict)

    # Build sfocu for performing checks with baseline data
    # for Composite and Comparison tests
    __buildSFOCU(mainDict)

    # Run flashTest - actually call the backend flashTest.py here
    __flashTest(apiDict,testDict,mainDict)

def __flashTest(apiDict,testDict,mainDict):
    """
    Run flashTest.py from backend/FlashTest

    Arguments:
    ----------
    Arguments:
    apiDict   : API dictionary
    testDict  : Test dictionary
    mainDict  : Main dictionary
    """
    # Create output directory for TestResults
    # if it does not exist
    os.system('mkdir -pv {0}'.format(mainDict['pathToOutdir']))

    # Run flashTest.py for each test in testDict
    for testName,testList in testDict.items():
        
        # Get pathToInfo for each testName
        mainDict['pathToInfo'] = __getTestInfo(apiDict['testDir'],testName,mainDict['flashSite'])

        # run backend/FlashTest/flashTest.py with desired configuration
        #
        testProcess = subprocess.run('python3 {0}/flashTest.py -z {1} -o {2} \
                                                               -c {3} -i {4} \
                                                               -v -L  -s {5} \
                                      {6}'.format(os.path.dirname(backend.FlashTest.__file__),
                                            mainDict['pathToFlash'],
                                            mainDict['pathToOutdir']+'/'+str(testName),
                                            mainDict['configFile'],
                                            mainDict['pathToInfo'],
                                            mainDict['flashSite'],
                                            " ".join(testList)), shell=True)


    # Clean up 'testDir/.fxt' directory
    subprocess.run('rm {0} {1}'.format(mainDict['pathToInfo'],mainDict['configFile']),shell=True)

    # Handle errors
    # TODO: Add checks to read logs and report error for each test
    # that failed
    if testProcess.returncode != 0:
        print('FlashTest returned exit status {0}'.format(exit_status))
        print('---------------------------------------------------------')
        raise ValueError

    else:
        print('FlashTest reports SUCCESS')

def __getMainDict(apiDict):
    """
    Arguments
    --------
    apiDict  : Dictionary to override values from Config file

    Returns
    -------
    mainDict: Dictionary for keys in the config file
    """
    # Build Config file for mainDict.
    # Read the user Config file (configApi), append it to Base Config from backend (configBase),
    # and create a new Config (configMain) in 'testDir/.fxt' folder
    configApi  = apiDict['configFile']
    configMain = str(apiDict['testDir'])+'/.fxt'+'/Config'
    configBase = os.path.dirname(backend.FlashTest.__file__)+'/configBase'

    # Create .fxt folder to write configMain
    subprocess.run('mkdir -pv {0}'.format(str(apiDict['testDir'])+'/.fxt'),shell=True)

    # Build configMain from configApi and configBase
    subprocess.run('cat {0} {1} > {2}'.format(configApi,configBase,configMain),shell=True)
 
    # Parse the configMain file
    mainDict=backend.FlashTest.lib.parseFile(configMain)

    # Update mainDict with values from apiDict
    for key,value in apiDict.items(): 
        if value and key in mainDict:
            mainDict[key] = value

    # Set configFile for mainDict
    mainDict['configFile'] = configMain

    return mainDict

def __buildSFOCU(mainDict):
    """
    Build SFOCU (Serial Flash Output Comparison Utility)

    Arguments:
    ----------
    mainDict: Dictionary from Config file
    """
    # Build brand new version of sfocu
    # cd into sfocu directory and compile a new 
    # version
    os.chdir('{0}/tools/sfocu'.format(mainDict['pathToFlash']))
    subprocess.run('make SITE={0} NO_NCDF=True sfocu clean'.format(mainDict['flashSite']),shell=True)
    subprocess.run('make SITE={0} NO_NCDF=True sfocu'.format(mainDict['flashSite']),shell=True)

def __getTestInfo(testDir,testName,flashSite):
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
    subprocess.run('mkdir -pv {0}'.format(str(testDir)+'/.fxt'),shell=True)

    # Set variables for testInfo and testSiteInfo
    testInfo = str(testDir)+'/{0}.xml'.format(testName)
    testSiteInfo = str(testDir)+'/.fxt'+'/test.info'.format(testName)

    # Build testSiteInfo from testInfo 
    # This done to 'trick' backend/FlashTest/flashTest.py
    # TODO: Find an elegant way to do this
    with open('{0}'.format(testSiteInfo), 'w') as testFile: testFile.write('<{0}>\n'.format(flashSite))
    os.system('cat {0} >> {1}'.format(testInfo,testSiteInfo))
    with open('{0}'.format(testSiteInfo), 'a') as testFile: testFile.write('</{0}>\n'.format(flashSite))

    return testSiteInfo
