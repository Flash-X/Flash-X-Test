#!/usr/bin/env python3
import sys, os, re

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

import xmlNode

datePat = re.compile("\d\d\d\d-\d\d-\d\d(?:_\d+)?")
soughtKeys = ["shortPathToBenchmark", "shortPathToBenchmarkDir"]

def extract(pathToInfoFile, nodePath=""):
  if not os.path.isfile(pathToInfoFile):
    print("'%s' either does not exist or is not a file" % pathToInfoFile)
    sys.exit(1)
  # else
  mn = xmlNode.parseXml(pathToInfoFile)
  if not mn.findChild(nodePath):
    print("'%s' does not lead to an node in '%s'"  % (nodePath, pathToInfoFile))
    sys.exit(1)
  # else
  mn = mn.findChild(nodePath)

  foundKeys = {}  # dictionary that will hold all keys for which we found at least 1 match
  bms = {}        # dictionary that will hold all unique benchmark-dates
  for sn in mn:
    for line in sn.text:
      for soughtKey in soughtKeys:
        if line.startswith(soughtKey):
          foundKeys[soughtKey] = None
          key, val = line.split(":",1)
          dates = datePat.findall(val)
          if dates:
            bms[dates[0]] = None
          else:
            print("warning: text of '%s' contains key '%s' but this key contains no date pattern" % (sn.getPathBelowRoot(), soughtKey))

  print("keys found: %s" % ", ".join(list(foundKeys.keys())))

  bms = list(bms.keys())  # transform to list
  bms.sort()
  for bm in bms:
    print(bm)

def usage():
  print("This program examines a info-file and prints a list of distinct")
  print("dates (invocation dirnames) to which the info-file makes reference")
  print("in its 'shortPathToBenchmark' and 'shortPathToBenchmarkDir' fields.")
  print("")
  print("usage: $ ./extractUniqueBenchmarks.py [path-to-info-file] [node-path]")
  print("")
  print("where 'path-to-info-file' is a path to the '.info' file and 'node-path'")
  print("is an optional argument that specifies a node below the master node of")
  print("the info file. If this argument is provided, the extraction of benchmark")
  print("dates will begin at the specified node.")
  sys.exit(0)

if __name__ == "__main__":
  if len(sys.argv) != 2 and len(sys.argv) != 3:
    usage()
  # else
  if len(sys.argv) == 2:
    extract(sys.argv[1])
  else:  # it must be 3
    extract(sys.argv[1], sys.argv[2])
