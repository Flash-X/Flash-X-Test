import argparse
import shlex

def parseTestSuite(testSuite):
    """
    Arguments
    ---------
    testSuite : String for testsuite filename
    """

    testSpecList = []

    with open(testSuite, "r") as testSpecFile:
        for line in testSpecFile:
            line=line.rstrip("\n")
            testSpecList.append(line.split("#")[0])

    testSpecList = [testSpec for testSpec in testSpecList if testSpec]

    testSuiteParser = argparse.ArgumentParser(description='Parser for test specification')
    testSuiteParser.add_argument("-t", "--test", help='Test node')
    testSuiteParser.add_argument("-n", "--nprocs", help='Num procs')
    testSuiteParser.add_argument('--debug', action="store_true")

    testSuiteParser.set_defaults(debug=False)

    testSuiteDict = {}

    for testSpec in testSpecList:
        testName = shlex.split(testSpec)[0]
        testArgs = testSuiteParser.parse_args(shlex.split(testSpec)[1:])
        testSuiteDict.update({testName : vars(testArgs)})

    return testSuiteDict


if __name__ == "__main__":
    testSuiteDict = parseTestSuite("testsuite")
    print(testSuiteDict)
