import argparse
import shlex

# Create a test suite parser
SuiteParser = argparse.ArgumentParser(description="Parser for test suite")
SuiteParser.add_argument("-t", "--test", help="Test node", type=str)
SuiteParser.add_argument("-np", "--nprocs", help="Num procs", type=int)
SuiteParser.add_argument(
    "-cbase", "--cbase", help="Date for comparison benchmark", type=str
)
SuiteParser.add_argument(
    "-rbase", "--rbase", help="Date for restart benchmark", type=str
)
SuiteParser.add_argument("-tol", "--tolerance", help="Error tolerance", type=float)
SuiteParser.add_argument(
    "-e", "--env", action="append", nargs="+", help="Environment variable", type=str
)
SuiteParser.add_argument("-debug", "--debug", action="store_true")
SuiteParser.add_argument(
    "-as", "--add-setup-opts", help="Additional setup options", type=str
)
SuiteParser.set_defaults(
    debug=False,
    nprocs=1,
    test="",
    env=None,
    cbase=None,
    rbase=None,
    tolerance=0.0,
    add_setup_opts="",
)


def continuationLines(fin):
    for line in fin:
        line = line.rstrip("\n")
        while line.endswith("\\"):
            line = line[:-1] + "\\" + next(fin).rstrip("\n")
        yield line

writelines = []
with open("Flash-X.suite", "r") as sfile:
     # loop over lines
     for line in continuationLines(sfile):
         splitLine = line.split("#")
         if splitLine[0]:
             print(splitLine[0])
             spec = shlex.split(splitLine[0])
             testArgs = SuiteParser.parse_args([value.replace("\t","") for value in spec][1:])
             testArgs.cbase = "newvalue"
             for index, option in enumerate(spec):
                 if "cbase" in option:
                     spec[index+1] = testArgs.cbase
             print(spec)
             #splitLine[0] = " ".join(spec)
         #writelines.append(f"{'#'.join(splitLine)}\n")
