"""FlashXTest library to interface with backend.FlashTest"""

import os

from ... import backend

def setup(apiDict):
    """
    Setup configuration

    Arguments
    ---------
    apiDict    : API dictionary
    """
    # Get path to configuration template from FlashTest backend
    configTemplate = os.path.dirname(backend.FlashTest.__file__)+'/configTemplate'

    # Get path to user configuration file from apiDict
    configFile = apiDict['configFile']

    # Start building configFile from configTemplate
    #
    # configTemplate in read mode as ctemplate
    # configFile in write mode as cfile
    #
    with open(configTemplate,'r') as ctemplate, open(configFile, 'w') as cfile:

       # Read lines from ctemplate
       lines = ctemplate.readlines()

       # Iterate over lines and set values defined in apiDict
       for line in lines:

            # Set default pathToOutdir
            line = line.replace("pathToOutdir:", str("pathToOutdir:       "+apiDict['testDir']+"/TestResults"))
 
            # Set 'pathToFlash' if defined in apiDict
            if 'pathToFlash' in apiDict: 
                line = line.replace("pathToFlash:", str("pathToFlash:        "+str(apiDict['pathToFlash'])))

            # Set 'flashSite' if define in apiDict
            if 'flashSite' in apiDict:
                line = line.replace("flashSite:", str("flashSite:          "+str(apiDict['flashSite'])))

            cfile.write(line)

    print("Initialized FlashXTest Configuration")
