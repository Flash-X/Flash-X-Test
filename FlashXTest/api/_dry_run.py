"""Python API for FlashXTest"""

import os
import subprocess
from .. import lib
from .. import backend


def show_tests(**apiDict):
    """
    Show all tests for a given setupname
    """
    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    # Get mainDict
    mainDict = lib.config.getMainDict(apiDict)

    # Get setup information from yaml file
    testDict = lib.yml.parseYaml(mainDict, mainDict["setupName"])

    for nodeName in testDict:
        print(f"\n{nodeName}")

        for key, value in testDict[nodeName].items():
            print(f"\t{key}: {value}")


def dry_run(run_test=False, **apiDict):
    """
    Compile a specific test using setupName and testNode
    """
    # Cache the value to current directory and set it as
    # testDir in apiDict
    apiDict["testDir"] = os.getcwd()

    # Cache the value of user Config file and store it as
    # pathToConfig in apiDict
    apiDict["pathToConfig"] = apiDict["testDir"] + "/config"

    # Get mainDict
    mainDict = lib.config.getMainDict(apiDict)

    # Get setup information from yaml file
    setupInfo = lib.yml.parseYaml(mainDict, mainDict["setupName"])[mainDict["nodeName"]]

    subprocess.run(
        f'cd {mainDict["pathToFlash"]} && '
        + f'./setup {mainDict["setupName"]} {setupInfo["setupOptions"]} '
        + f'-site={mainDict["flashSite"]} -objdir={mainDict["objDir"]} && '
        + f'cd {mainDict["objDir"]} && make -j',
        shell=True,
        check=True,
    )

    if run_test:

        parfile = "flash.par"

        parfile_path = (
            mainDict["pathToFlash"]
            + os.sep
            + "source/Simulation/SimulationMain"
            + os.sep
            + mainDict["setupName"]
            + os.sep
            + parfile
        )

        if "parfiles" in setupInfo.keys():
            parfiles_list = setupInfo["parfiles"].split(" ")
            if len(parfiles_list) > 1:
                raise ValueError(
                    lib.colors.FAIL
                    + f'[FlashXTest] {mainDict["nodeName"]} for {mainDict["setupName"]} '
                    + f"contains multiple parfiles"
                )
            else:
                parfile = parfiles_list[0]

                parfile_path = (
                    mainDict["pathToFlash"]
                    + os.sep
                    + "source/Simulation/SimulationMain"
                    + os.sep
                    + mainDict["setupName"]
                    + os.sep
                    + "tests"
                    + os.sep
                    + parfile
                )

        subprocess.run(
            f'cd {mainDict["pathToFlash"]}/{mainDict["objDir"]} && '
            + f"cp {parfile_path} . && "
            + f'mpirun -n {mainDict["numProcs"]} ./flashx -par_file {parfile}',
            shell=True,
            check=True,
        )
