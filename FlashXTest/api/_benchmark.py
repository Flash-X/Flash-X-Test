"""Python API for FlashXTest"""

import os
from datetime import date
import subprocess
from .. import lib


def benchmark(**apiDict):
    """
    Initialize test configuration

    Arguments
    ---------
    apiDict : Dictionary to populate Config file
    """
    if apiDict["testList"] and apiDict["allTests"]:
        print(lib.colors.FAIL + "[FlashXTest] TEST_LIST should be empty with --all")

    else:
        # Cache the value to current directory and set it as
        # testDir in apiDict
        apiDict["testDir"] = os.getcwd()

        # Cache the value of user Config file and store it as
        # pathToConfig in apiDict
        apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

        # Get mainDict for performing tests. This will read
        # the user Config file and set values that
        # were not provided in apiDict and override values
        # that were
        mainDict = lib.config.getMainDict(apiDict)

        # Create directory for benchmark
        try:
            os.makedirs(
                os.path.join(
                    mainDict["baselineDir"],
                    mainDict["flashSite"],
                    date.today().isoformat(),
                )
            )
        except FileExistsError:
            pass

        if apiDict["allTests"]:
            subprocess.run(
                f"cp -r "
                + f'{os.path.join(mainDict["pathToOutdir"], mainDict["flashSite"], date.today().isoformat(),"*")} '
                + f'{os.path.join(mainDict["baselineDir"], mainDict["flashSite"], date.today().isoformat())}',
                shell=True,
                check=True,
            )

        elif apiDict["testList"]:
            for test in apiDict["testList"]:
                subprocess.run(
                    f"cp -r "
                    + f'{os.path.join(mainDict["pathToOutdir"], mainDict["flashSite"], date.today().isoformat(), test.replace("/","_"))} '
                    + f'{os.path.join(mainDict["baselineDir"], mainDict["flashSite"], date.today().isoformat())}',
                    shell=True,
                    check=True,
                )

        else:
            print(
                lib.colors.WARNING
                + "[FlashXTest] No value supplied to create benchmark"
            )
