import argparse
import shlex

testSpecList = []

with open("testsuite", "r") as testSpecFile:
    for line in testSpecFile:
        line=line.rstrip("\n")
        testSpecList.append(line.split("#")[0])

testSpecList = [testSpec for testSpec in testSpecList if testSpec]

testParser = argparse.ArgumentParser(description='Parser for test specification')
testParser.add_argument("-t", "--test", help='Test node')
testParser.add_argument("-n", "--nprocs", help='Num procs')

testSuite = {}

for testSpec in testSpecList:
    testName = shlex.split(testSpec)[0]
    testArgs = testParser.parse_args(shlex.split(testSpec)[1:])
    testSuite.update({testName : vars(testArgs)})

print(testSuite)
