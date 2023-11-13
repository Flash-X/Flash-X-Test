"""Python API for FlashXTest"""

import os
import subprocess
from .. import lib
from .. import backend


def show_specs(setupName):
    """
    Show all tests for a given setupname

    Arguments
    ---------
    setupName : Name of Flash-X simulation/setup
    """
    apiDict = locals()
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()

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
        apiDict["log"].brk()
        apiDict["log"].info(f"{nodeName}")

        for key, value in testDict[nodeName].items():
            apiDict["log"].info(f"\t{key}: {value}")


def dry_run(
    setupName,
    nodeName,
    numProcs,
    objDir=os.path.join(os.getcwd(), "objdir"),
    runTest=True,
):
    """
    Compile a specific test using setupName and testNode

    Arguments
    ---------
    setupName	: Flash-X setup name
    nodeName	: Test node key
    numProcs	: Number of processors
    objDir	: Object directory
    runTest     : True/False
    """
    apiDict = locals()
    apiDict["log"] = backend.FlashTest.lib.logfile.ConsoleLog()

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

    if runTest:

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
