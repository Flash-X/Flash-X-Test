#!/usr/bin/env python
import sys, os
import cgi, re
sys.path.insert(0, "../lib")
import littleParser, ezt

class Checkfile:
  """
  encapsulates the data needed to locate a checkpoint file
  """
  def __init__(self, queryStr, filename):
    self.queryStr = queryStr
    self.filename = filename

class FlashRun:
  """
  encapsulates one run of the Flash code against
  a single parfile. A list of FlashRun objects
  will form part of the data dictionary passed to
  the ezt template
  """
  def __init__(self, name):
    self.name = name

class Parfile:
  """
  encapsulates the data needed to locate parameter files
  """
  def __init__(self, queryStr, filename):
    self.queryStr = queryStr
    self.filename = filename

class Logfile:
  """
  encapsulates the data needed to locate log files
  """
  def __init__(self, path, filename):
    self.path = path
    self.filename = filename

class Datfile:
  """
  encapsulates the data needed to locate .dat files
  """
  def __init__(self, path, filename):
    self.path = path
    self.filename = filename


# -------------- form data ---------------- #
form = cgi.FieldStorage()

targetDir = form.getvalue("target_dir")

# the data dictionary we will pass to the ezt template
templateData = {}

# fill in data that has to do with this build
# (i.e. setup and compilation data)
templateData["buildDir"]            = os.path.basename(targetDir)
templateData["invocationDir"]       = os.path.basename(os.path.dirname(targetDir))
templateData["pathToInvocationDir"] = os.path.dirname(targetDir)

# was there a "test.info" file associated with this build?
pathToInfoFile = os.path.join(targetDir, "test.info")
if os.path.isfile(pathToInfoFile):
  templateData["pathToInfoFile"] = pathToInfoFile
else:
  templateData["pathToInfoFile"] = None

# is there a "deleted_files" file?
pathToDeletedFiles = os.path.join(targetDir, "deleted_files")
if os.path.isfile(pathToDeletedFiles):
  templateData["pathToDeletedFiles"] = pathToDeletedFiles
else:
  templateData["pathToDeletedFiles"] = None

# a link back to the logfile for this invocation of
# flash test if no data is available
pathToFlashTestLog = os.path.join(os.path.dirname(targetDir), "flash_test.log")
if os.path.isfile(pathToFlashTestLog):
  templateData["pathToFlashTestLog"] = pathToFlashTestLog
else:
  templateData["pathToFlashTestLog"] = None


pathToErrorsFile = os.path.join(targetDir, "errors")
# parse errors file
errorLines = []
if os.path.isfile(pathToErrorsFile):
  errorLines = open(pathToErrorsFile).read().strip().split("\n")

if len(errorLines) > 0 and int(errorLines[0]) > 0:
  templateData["setupFailed"] = True
else:
  templateData["setupFailed"] = None

if len(errorLines) > 0 and int(errorLines[1]) > 0:
  templateData["gmakeFailed"] = True
else:
  templateData["gmakeFailed"] = None


pathToSetupCall = os.path.join(targetDir, "setup_call")
if os.path.isfile(pathToSetupCall):
  templateData["setupCall"] = open(pathToSetupCall, "r").read()
else:
  templateData["setupCall"] = None

pathToSetupOutput = os.path.join(targetDir, "setup_output")
if os.path.isfile(pathToSetupOutput):
  templateData["pathToSetupOutput"] = pathToSetupOutput
else:
  templateData["pathToSetupOutput"] = None

pathToSetupError = os.path.join(targetDir, "setup_error")
if os.path.isfile(pathToSetupError):
  templateData["pathToSetupError"] = pathToSetupError
else:
  templateData["pathToSetupError"] = None

if ((templateData["setupFailed"]) or
    (templateData["pathToSetupOutput"] and os.stat(templateData["pathToSetupOutput"])[6] > 0)):
  templateData["showSetup"] = True
else:
  templateData["showSetup"] = None

pathToFlashH = os.path.join(targetDir, "Flash.h")
if os.path.isfile(pathToFlashH):
  templateData["pathToFlashH"] = pathToFlashH
else:
  templateData["pathToFlashH"] = None


pathToGmakeCall = os.path.join(targetDir, "gmake_call")
if os.path.isfile(pathToGmakeCall):
  templateData["pathToGmakeCall"] = pathToGmakeCall
else:
  templateData["pathToGmakeCall"] = None

pathToGmakeOutput = os.path.join(targetDir, "gmake_output")
if os.path.isfile(pathToGmakeOutput):
  templateData["pathToGmakeOutput"] = pathToGmakeOutput
else:
  templateData["pathToGmakeOutput"] = None

pathToCompilationTime = os.path.join(targetDir, "compilation_time")
if os.path.isfile(pathToCompilationTime):
  templateData["compilationTime"] = open(pathToCompilationTime, "r").read()
else:
  templateData["compilationTime"] = None

pathToGmakeError = os.path.join(targetDir, "gmake_error")
if os.path.isfile(pathToGmakeError):
  templateData["pathToGmakeError"] = pathToGmakeError
else:
  templateData["pathToGmakeError"] = None

if ((templateData["gmakeFailed"]) or
    (templateData["pathToGmakeOutput"] and os.stat(templateData["pathToGmakeOutput"])[6] > 0)):
  templateData["showCompilation"] = True
else:
  templateData["showCompilation"] = None


# we assume any directories in 'targetDir' to be the output
# of a single *run* of Flash (i.e., the output resulting from
# the Flash executable's being run against a single parfile)
# Information in this directory will be stored in a FlashRun
# object (see class definition at top of file)
runs = [FlashRun(item) for item in os.listdir(targetDir)
        if os.path.isdir(os.path.join(targetDir, item))]

if len(runs) > 0:
  if len(runs) == 1:
    templateData["numParfiles"] = "1 parfile"
  else:
    templateData["numParfiles"] = "%s parfiles" % len(runs)

  # fill in the FlashRun object's members with
  # information specific to this single run
  for run in runs:
    run.fullPath      = os.path.join(targetDir, run.name)
    run.checkfiles    = []
    run.datfiles=[]      
    run.logfiles=[]       
    run.pathToParfiles = []
    run.pathToAmrRuntimeParameters     = None
    run.pathToAmrRuntimeParametersDump = None

    items = os.listdir(run.fullPath)
    for item in items:
      if re.match(".*?_chk_\d+$", item):
        checkfileQueryStr = "target_file=%s" % os.path.join(run.fullPath, item)
        run.checkfiles.append(Checkfile(checkfileQueryStr, item))
      elif item.endswith(".dat"):
        pathToDatfile = os.path.join(run.fullPath, item)
	run.datfiles.append(Datfile(pathToDatfile,item))
      elif item.endswith(".log") and not item == "amr.log":
        pathToLogfile = os.path.join(run.fullPath, item)
	run.logfiles.append(Logfile(pathToLogfile,item))
      elif item.endswith(".par"):
        parfileQueryStr = os.path.join(run.fullPath, item)
        run.pathToParfiles.append(Parfile(parfileQueryStr, item))
      elif item == "amr_runtime_parameters":
        run.pathToAmrRuntimeParameters     = os.path.join(run.fullPath, item)
      elif item == "amr_runtime_parameters.dump":
        run.pathToAmrRuntimeParametersDump = os.path.join(run.fullPath, item)

    run.checkfiles.sort()

    # parse data for number of processors and wall-clock time into a dictionary.
    run.numProcs      = None
    run.wallClockTime = None
    run.numCheckfiles = "0 checkfiles"

    pathToRunSummary = os.path.join(run.fullPath, "run_summary")
    if os.path.isfile(pathToRunSummary):
      runSummaryDict = littleParser.parseFile(pathToRunSummary)

      if "numProcs" in runSummaryDict:
        if runSummaryDict["numProcs"] == "1":
          run.numProcs = "1 processor"
        else:
          run.numProcs = "%s processors" % runSummaryDict["numProcs"]

      if "wallClockTime" in runSummaryDict:
        run.wallClockTime = runSummaryDict["wallClockTime"]

      if "numCheckfiles" in runSummaryDict:
        numCheckfiles = int(runSummaryDict["numCheckfiles"].strip())
        if numCheckfiles == 1:
          run.numCheckfiles = "1 checkfile"
        else:
          run.numCheckfiles = "%s checkfiles" % numCheckfiles

    run.runFailed           = None
    run.testFailed          = None
    run.changedFromPrevious = None

    pathToErrorsFile = os.path.join(run.fullPath, "errors")
    if os.path.isfile(pathToErrorsFile):
      errorLines = open(pathToErrorsFile).read().strip().split("\n")

      # A "!" at the end of the errors file means at least
      # one run in this build had testing results different
      # from the same run from the previous invocation.
      if len(errorLines) == 3 and errorLines[2].strip() == "!":
        run.changedFromPrevious = True

      if int(errorLines[0].strip()) > 0:
        run.runFailed = True
      elif int(errorLines[1].strip()) > 0:
        run.testFailed = True

    pathToFlashCall = os.path.join(run.fullPath, "flash_call")
    if os.path.isfile(pathToFlashCall):
      run.pathToFlashCall = pathToFlashCall
    else:
      run.pathToFlashCall = None

    pathToFlashOutput = os.path.join(run.fullPath, "flash_output")
    if os.path.isfile(pathToFlashOutput):
      run.pathToFlashOutput = pathToFlashOutput
    else:
      run.pathToFlashOutput = None

    pathToFlashError = os.path.join(run.fullPath, "flash_error")
    if os.path.isfile(pathToFlashError):
      run.pathToFlashError = pathToFlashError
    else:
      run.pathToFlashError = None

    pathToDeletedFiles = os.path.join(run.fullPath, "deleted_files")
    if os.path.isfile(pathToDeletedFiles):
      run.pathToDeletedFiles = pathToDeletedFiles
    else:
      run.pathToDeletedFiles = None

    if ((run.runFailed) or
        (run.pathToFlashOutput and os.stat(run.pathToFlashOutput)[6] > 0)):
      run.showRun = True
    else:
      run.showRun = None

    pathToTestOutput = os.path.join(run.fullPath, "test_output")
    if os.path.isfile(pathToTestOutput) and os.stat(pathToTestOutput)[6] > 0:
      run.testOutput = open(pathToTestOutput).read().strip().replace("\n","<br>")
    else:
      run.testOutput = None

    if (run.testFailed or run.testOutput):
      run.showTest = True
    else:
      run.showTest = None

  templateData["runs"] = runs
else:
  templateData["numParfiles"] = None
  templateData["runs"] = None

print("Content-type: text/html\n")
print("<html>")
print("<head>")
print("<title>Flash Center for Computational Science</title>")
print(open("viewBuildStyle.css","r").read())
print("</head>")
# print the html generated by ezt templates
ezt.Template("viewBuildTemplate.ezt").generate(sys.stdout, templateData)
print("</html>")
