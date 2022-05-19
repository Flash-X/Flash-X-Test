import io
import os, re, subprocess, time, datetime, sys
import secondsToHuman
import shutil

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

from getProcessResults import getProcessResults
from strategyTemplates import *
from xmlNode import *
import flashTestParser as parser

######################################
##  PRE-PROCESS, SETUP, COMPILE, &  ##
##  EXECUTE FOR ALL FLASH PROBLEMS  ##
######################################

def __abort(msg):
  sys.stderr.write(msg)
  sys.exit(1)

def _write_to_file(filename, mode, text, encoding=None, errors=None):
    """
    Helper function for writing a text in memory to a file.

    The file of the given filename is opened with the given mode and, if
    appropriate, with the given encoding and errors parameters; text is
    written to it; then the file is closed.


    This helper exists so that this file can be used in both Python2 (as
    long as it is not too ancient) and Python3.  In the Python3 case,
    the text should always be given as a string; the function may also
    work for a binary buffer, but that has not been tested.  In the
    Python2 case, this routine should work for text being either a
    unicode string or a regular string; in the latter case, the encoding
    and error parameters are ignored.

    There are many places in the code below that follow the pattern

       [io.]open( <filename>, <other arguments> ).write( <something> )

    were this function could be used instead of the existing code.  That
    might even make the code more readable.  Currently, the instances
    where the pattern has been replaced by a call to this function are
    mostly those where version compatibility problems were either
    observed or are suspected.
    """
    try:                        # u"" may be unrecognized in early python33 versions
        isU = (type(text) == type(u""))
    except SyntaxError:
        isU = (type(text) == type("")) and (type(text) != type(b""))
    if isU:
        with io.open(filename, mode, encoding=encoding, errors=errors) as f:
            f.write(text)
    else: # if type(text) == type(b""):
        with open(filename, mode) as f:
            f.write(text)

def splitHostAndPath(path):
  if path.count(':') > 0:
    return path.split(':', 1)
  else:
    return None, path
def joinHostAndPath(host,path):
  if host:
    return host + ":" + path
  else:
    return path

def pullfile(path,log):
  if path.count(':') > 0:
    host, path = path.split(':', 1)
  else:
    return path
  tmp = 'delete_me-%x' % hash(path)
  log.stp("Pulling %s:%s to %s" % (host, path, tmp))
  #print 'pulling %s: %s' % (tmp,path)
  out, err, duration, exitStatus = getProcessResults("scp %s:%s %s" % (host, path, tmp))
  if err:       #__abort("Unable to retrieve \"%s:%s\"\n%s" % (host, path, err))
    log.err("Unable to retrieve \"%s:%s\"\n%s" % (host, path, err))
    return None

  if exitStatus != 0:      #__abort("Exit status %s indicates error retrieving \"%s:%s\"" % (exitStatus, host, path))
    log.err("Exit status %s indicates error retrieving \"%s:%s\"" % (exitStatus, host, path))
    return None

  if not os.path.isfile(tmp): #__abort("File \"%s\" not found" % tmp)
    log.err("File \"%s\" not found" % tmp)
    return None

  f = open(tmp+'_mtime', 'w')
  f.write(str(os.path.getmtime(tmp)))
  f.close()
  return os.path.join(os.getcwd(),tmp)

def pushfile(path):
  if path.count(':') > 0:
    host, path = path.split(':', 1)
  else:
    return
  tmp = 'delete_me-%x' % hash(path)
  if os.path.isfile(tmp):
    f = open(tmp+'_mtime', 'r')
    mt0 = f.read()
    f.close()
    if mt0 != str(os.path.getmtime(tmp)):
      out, err, duration, exitStatus = getProcessResults("scp %s %s:%s" % (tmp, host, path))
      if err: __abort("Unable to send \"%s:%s\"\n%s" % (host, path, err))
      if exitStatus != 0: __abort("Exit status %s indicates error sending \"%s:%s\"" % (exitStatus, host, path))
    os.remove(tmp)
    os.remove(tmp+'_mtime')

class FlashEntryPoint(EntryPointTemplate):
  def entryPoint1(self):
    log           = self.masterDict["log"]            # guaranteed to exist by flashTest.py
    flashTestOpts = self.masterDict["flashTestOpts"]  # guaranteed to exist by flashTest.py

    ##############################
    ##  CHECK FOR FLASH SOURCE  ##
    ##############################

    pathToFlash = flashTestOpts.get("-z","")
    if not pathToFlash:
      # check if we got a path to FLASH from the config file
      pathToFlash = self.masterDict.get("pathToFlash","")
      # make sure we have an absolute path
      if pathToFlash and not os.path.isabs(pathToFlash):
        pathToFlash = os.path.join(pathToFlashTest, pathToFlash)
    else:
      # make sure we have an absolute path
      if not os.path.isabs(pathToFlash):
        pathToFlash = os.path.join(os.getcwd(), pathToFlash)

    if not pathToFlash:
      log.err("You must provide a path to a copy of the FLASH source\n" +
              "either in a \"config\" file or with the \"-z\" option.")
      return False
    elif not os.path.isdir(pathToFlash):
      if "-u" in flashTestOpts:
        log.warn("\"%s\" does not exist or is not a directory." % pathToFlash)
      else:
        log.err("\"%s\" does not exist or is not a directory." % pathToFlash)

    self.masterDict["pathToFlash"] = pathToFlash

    ####################################
    ##  UPDATE FLASH SOURCE IF ASKED  ##
    ####################################

    pathToInvocationDir = self.masterDict["pathToInvocationDir"]  # guaranteed to exist by flashTest.py

    if "-u" in flashTestOpts:

      updateScript = self.masterDict.get("updateScript","").strip()
      if updateScript:

        # Capture the differences between tester's local working copy
        # and the HEAD revision unless those differences are too long.
        diffFlash = self.masterDict.get("diffFlash","").strip()
        if diffFlash:
          log.stp("Attempting to 'diff' this working copy and the HEAD repository revision\n" +
                  "with \"%s\"" % diffFlash)
          diffOut = ("output from \"%s\":\n" % diffFlash +
                     "**************" + "*"*len(diffFlash) + "\n")
          # We have to use popen for this instead of "getProcessResults" because
          # we're redirecting the output of the "diffFlash" command through a pipe,
          # and the pseudoterminals of "getProcessResults" don't deal well with those.
          p = subprocess.Popen([diffFlash + " | wc"],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,close_fds=True)
          p.wait()
          out = p.stdout.read().strip()
          size = int(out.split()[2])
          if size < 10000000:  # ~10 MB
            # the word count from "wc" was ok, so we can go back to using "getProcessResults"
            diffOut += (getProcessResults(diffFlash)[0] + "\n")
          else:
            diffOut += "Byte count from <diffFlash> is too long. Skipping this step.\n"
        else:
          diffOut = ""

        log.stp("Attempting to update FLASH source at \"%s\" with \"%s\"" % (pathToFlash, updateScript))

        cwd = os.getcwd()
        if (updateScript[0:3] != "rm "): os.chdir(pathToFlash)

        out, err, duration, exitStatus = getProcessResults(updateScript)
        if exitStatus != 0:
          open(os.path.join(pathToInvocationDir, "update_output"),
               "w",
          ).write(diffOut)
          if (updateScript[0:3] != "rm "): os.chdir(cwd)
          log.err("Exit status %s indicates error updating FLASH source..." % exitStatus)
          if (err != ""):
            log.info("stderr: " + err)
          if (out != "") and (out != err):
            log.info("stdout: " + out)
          return False
        else:
          log.info("FLASH source was successfully updated")
          open(os.path.join(pathToInvocationDir, "update_output"),
               "w",
          ).write(diffOut + out)

        os.chdir(cwd)
      else:
        log.err("\"-u\" passed to command line but no key \"updateScript\"\n" +
                "found in \"config\". Unable to update FLASH source")
        return False
    else:
      log.warn("FLASH source at \"%s\" was not updated" % pathToFlash)

    return True


  def entryPoint2(self):
    testPath = self.masterDict["testPath"]  # guaranteed to exist by flashTest.py
    firstElement = testPath.split("/",1)[0]

    # If this is a Default test, give it a special setupper component
    # (will be be automatically installed based on value in 'masterDict')
    if firstElement == "Default":
      self.masterDict["setupper"] = "DefaultSetupper"

    # Write some info into "linkAttributes" for use by FlashTestView
    if firstElement == "Comparison" or "Composite":
      pathToBuildDir = self.masterDict["pathToBuildDir"]  # guaranteed to exist by flashTest.py
      tester = self.masterDict.get("tester", "SfocuTester")
      text = "testerClass: %s" % tester
      _write_to_file(os.path.join(pathToBuildDir, "linkAttributes"),
                     "w",
                     text,
                     errors="backslashreplace")


  def entryPoint3(self):
    testPath = self.masterDict["testPath"]  # guaranteed to exist by flashTest.py
    firstElement = testPath.split("/",1)[0]

    # give this test an appropriate executer component (will be
    # be automatically installed based on value in 'masterDict')
    if firstElement == "Comparison":
      self.masterDict["executer"] = "ComparisonExecuter"
    elif firstElement == "Restart":
      self.masterDict["executer"] = "RestartExecuter"
    elif firstElement == "Composite":
      self.masterDict["executer"] = "CompositeExecuter"

    # give this test an appropriate tester component (will be
    # be automatically installed based on value in 'masterDict')
    if firstElement == "Comparison":
      tester = self.masterDict.get("tester")
      if tester == "GridDumpTester":
        self.masterDict["tester"] = "GridDumpTester"
      else:
        self.masterDict["tester"] = "SfocuTester"
    elif firstElement == "Restart":
      self.masterDict["tester"] = "RestartTester"
    elif firstElement == "UnitTest":
      self.masterDict["tester"] = "UnitTester"
    elif firstElement == "Composite":
      tester = self.masterDict.get("tester")
      if tester == "CompositeTesterExperimentalIO":
        self.masterDict["tester"] = "CompositeTesterExperimentalIO"
      else:
        self.masterDict["tester"] = "CompositeTester"


class FlashSetupper(SetupperTemplate):
  def setup(self):
    """
    run the FLASH setup script

                log: pointer to FlashTest logfile object
        pathToFlash: abs path to top-level FLASH directory
                     containing all code pertaining to FLASH setups
     pathToBuildDir: abs path to the output dir for this build
    pathToFlashTest: abs path to the top-level FlashTest directory
          setupName: name of this Flash setup (Sod, Sedov, etc.)
       setupOptions: options passed to Flash setup script
    """
    log             = self.masterDict["log"]              # guaranteed to exist by flashTest.py
    pathToFlash     = self.masterDict["pathToFlash"]      # guaranteed to exist by flashTest.py
    pathToBuildDir  = self.masterDict["pathToBuildDir"]   # guaranteed to exist by flashTest.py
    pathToFlashTest = self.masterDict["pathToFlashTest"]  # guaranteed to exist by flashTest.py

    setupName      = self.masterDict.get("setupName","")
    setupOptions   = self.masterDict.get("setupOptions","")
    #providing a more general way of choosing a nondefault makefile -PR
    flashMakefile  = self.masterDict.get("flashMakefile","")

    if len(setupName) == 0:
      log.err("No setup name provided.\n" +
              "Skipping this build.")
      return False

    #if this is defined, go with nondefault makefile.
    if len(flashMakefile) != 0:
      setupOptions += " -makefile="
      setupOptions += flashMakefile

    pathToDotSuccess = os.path.join(pathToFlash, "object", ".success")
    if os.path.isfile(pathToDotSuccess):
      os.remove(pathToDotSuccess)

    # setup script
    pathToFlashSetupScript = os.path.join(pathToFlash, self.masterDict.get("setupExec","setup"))
    script = "%s %s %s" % (pathToFlashSetupScript, setupName, setupOptions)

    # record setup invocation
    _write_to_file(os.path.join(pathToBuildDir, "setup_call"), "w",
                   script,
                   errors="backslashreplace")

    # log timestamp of command
    log.stp(script)

    # cd to FLASH source
    os.chdir(pathToFlash)

    # get stdout/stderr and duration of setup and write to file
    out, err, duration, exitStatus = getProcessResults(script)
    io.open(os.path.join(pathToBuildDir, "setup_output"), "w",
            errors="backslashreplace",
    ).write(out)
    if len(err) > 0:
        io.open(os.path.join(pathToBuildDir, "setup_error"), "w",
                errors="backslashreplace",
        ).write(err)

    # cd back to flashTest
    os.chdir(pathToFlashTest)

    # return the success or failure of the setup
    if os.path.isfile(pathToDotSuccess):
      log.stp("setup was successful")
      os.remove(pathToDotSuccess)
      return True
    else:
      log.stp("setup was not successful")
      return False


class FlashCompiler(CompilerTemplate):
  def compile(self):
    """
    compile FLASH

       pathToFlash: abs path up to the top-level FLASH directory
    pathToBuildDir: abs path up to the output dir for this build
       pathToGmake: abs path to the gmake utility
           exeName: name to be given to the FLASH executable
    """
    log             = self.masterDict["log"]              # guaranteed to exist by flashTest.py
    pathToFlash     = self.masterDict["pathToFlash"]      # guaranteed to exist by flashTest.py
    pathToBuildDir  = self.masterDict["pathToBuildDir"]   # guaranteed to exist by flashTest.py
    pathToFlashTest = self.masterDict["pathToFlashTest"]  # guaranteed to exist by flashTest.py

    pathToGmake    = self.masterDict.get("pathToGmake", "gmake")
    exeName        = self.masterDict.get("exeName", "flash-exe")

    pathToDotSuccess = os.path.join(pathToFlash, "object", ".success")
    if os.path.isfile(pathToDotSuccess):
      os.remove(pathToDotSuccess)

    # determine gmake invocation and record it in "gmake_call" file and in log
    script = "%s EXE=%s" % (pathToGmake, os.path.join(pathToBuildDir, exeName))
    _write_to_file(os.path.join(pathToBuildDir, "gmake_call"), "w",
                   script,
                   errors="backslashreplace")
    log.stp(script)

    # we'll try to compile multiple times if the compilation fails
    # because of a problem with the license manager
    numTries = 0
    mode = "w"

    while numTries < 3:

      # cd to FLASH source object directory for compilation
      os.chdir(os.path.join(pathToFlash, "object"))

      # get stdout/stderr and duration of compilation and write to file
      out, err, duration, exitStatus = getProcessResults(script)
      io.open(os.path.join(pathToBuildDir, "gmake_output"), mode,
              encoding="utf-8", errors="backslashreplace",
      ).write(out)
      if len(err) > 0:
          io.open(os.path.join(pathToBuildDir, "gmake_error"), mode,
                  errors="backslashreplace",
          ).write(err)

      # cd back to flashTest
      os.chdir(pathToFlashTest)

      # return the success or failure of the compilation

      if os.path.isfile(pathToDotSuccess):
        log.stp("compilation was successful")
        # record compilation time in "compilation_time" file and in log
        duration = secondsToHuman.convert(duration)
        open(os.path.join(pathToBuildDir, "compilation_time"),
             "w",
        ).write(duration)
        log.info("duration of compilation: %s" % duration)
        self.masterDict["pathToFlashExe"] = os.path.join(pathToBuildDir, exeName)  # for exeScript
        os.remove(pathToDotSuccess)
        return True
      elif out.find("www.macrovision.com") > 0:
        log.stp("compilation failed due to licensing problem. Trying again...")
        numTries += 1
      elif out.find("Unable to obtain license: license not found") > 0:
        log.stp("compilation failed due to license problem. Trying again...")
        numTries += 1
        mode = "a"
      else:
        break

    log.stp("compilation was not successful")
    return False

  def getDeletePatterns(self):
    return [self.masterDict.get("exeName", "flash-exe")]


class FlashExecuter(ExecuterTemplate):
  def execute(self, timeout=None):
    """
    run the FLASH executable piping output and other data into 'runDir'

    pathToRunDir: abs path to output dir for this unique executable/parfile combination
        numProcs: number of processors used for this run
         parfile: name of the parfile to be used in this run
    """
    log             = self.masterDict["log"]              # guaranteed to exist by flashTest.py
    pathToFlash     = self.masterDict["pathToFlash"]      # guaranteed to exist by flashTest.py
    pathToRunDir    = self.masterDict["pathToRunDir"]     # guaranteed to exist by flashTest.py
    pathToFlashTest = self.masterDict["pathToFlashTest"]  # guaranteed to exist by flashTest.py
    pathToExeScript = self.masterDict["pathToExeScript"]  # guaranteed to exist by flashTest.py

    # read the execution script from "exeScript"
    exeScriptFile = os.path.join(pathToFlashTest, pathToExeScript)
    if not os.path.isfile(exeScriptFile):
      log.err("File \"exeScript\" not found. Unable to run executable.\n" +
              "Skipping all runs.")
      return False

    lines = open(exeScriptFile).read().split("\n")
    lines = [line.strip() for line in lines
             if len(line.strip()) > 0 and not line.strip().startswith("#")]
    script = "\n".join(lines)
    self.masterDict["script"] = script
    script = self.masterDict["script"]  # do it this way so that any angle-bracket variables
                                        # in "exeScript" will be filled in by self.masterDict
    # determine 'pathToRunSummary'
    pathToRunSummary = os.path.join(pathToRunDir, "run_summary")

    # cd to output directory to run executable
    os.chdir(pathToRunDir)

    # obtain and record number of processors
    if not self.masterDict.has_key("numProcs"):
      self.masterDict["numProcs"] = 1
    open(pathToRunSummary,
         "a",
    ).write("numProcs: %s\n" % self.masterDict["numProcs"])

    # record mpirun invocation in "flash_call" file and in log
    _write_to_file(os.path.join(pathToRunDir, "flash_call"),
                   "w",
                   script,
                   errors="backslashreplace",
    )
    log.stp(script)

    # get stdout/stderr and duration of execution and write to file
    out, err, duration, exitStatus = getProcessResults(script, timeout)

    io.open(os.path.join(pathToRunDir, "flash_output"), "a",
            errors="ignore",
    ).write(out)
    if len(err) > 0:
        io.open(os.path.join(pathToRunDir, "flash_error"), "a",
                errors="backslashreplace",
        ).write(err)

    # record execution time in the run summary and logfile in human-readable form
    duration = secondsToHuman.convert(duration)
    open(pathToRunSummary, "a").write("wallClockTime: %s\n" % duration)
    log.info("duration of execution: %s" % duration)

    # search the parfile output directory for checkpoint files
    checkFiles = []
    items = os.listdir(pathToRunDir)
    for item in items:
      if re.match(".*?_chk_\d+$", item):
        checkFiles.append(item)

    # record number and names of checkpoint files in the run summary
    open(pathToRunSummary, "a").write("numCheckfiles: %s\n" % len(checkFiles))
    for checkFile in checkFiles:
        open(pathToRunSummary, "a").write("checkFile: %s\n" % checkFile)

    # An exit status of 0 means a normal termination without errors.
    if exitStatus == 0:
      log.stp("Process exit-status reports execution successful")
      runSucceeded = True
    else:
      log.stp("Process exit-status reports execution failed")
      pathToFlashExe = self.masterDict["pathToFlashExe"]  # set by FlashCompiler, above
      if len(pathToFlashExe) > 0 and pathToFlashExe[0] == '/':
        time.sleep(1)
        killallCmd = 'killall -v -HUP %s' % pathToFlashExe
#        log.stp('killallCmd is "%s"' % killallCmd)
        p = subprocess.Popen([killallCmd],shell=True,stderr=subprocess.PIPE,close_fds=True)
        killStatus = p.wait()
        if killStatus==0:
          out = p.stderr.read().strip()
          if len(out) > 0:
            log.stp(killallCmd)
            log.info(out)
#        else:
#          log.stp("Exit status %d from %s" % (killStatus, killallCmd))
      else:
        log.stp('pathToFlashExe is "%s"' % pathToFlashExe)
      runSucceeded = False

    # cd back to flashTest
    os.chdir(pathToFlashTest)

    return runSucceeded

  def getDeletePatterns(self):
    deletePatterns = self.masterDict.get("deletePatterns", [])
    if len(deletePatterns) > 0:
      # split 'deletePatterns' into a list on whitespace
      deletePatterns = re.split("\s+",deletePatterns.strip())

    deletePatterns.extend([".*_chk_\d+$", ".*_plt_cnt_\d+$"])
    return deletePatterns


class ComparisonExecuter(FlashExecuter):
  def adjustFilesToDelete(self, filesToDelete):
    """
    Determine the highest-numbered checkpoint file and create an
    entry "chkMax" in masterDict whose value is the name of this
    file. We'll use this value later to do our sfocu comparison.

    Then remove this file's name from 'filesToDelete', which will
    later be used to determine which files will be deleted before
    creation of the slim copy of the invocation's output.
    """
    pathToRunDir = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py
    chkFiles = []

    # Search 'runDir' for checkpoint files. This method will also
    # be called for GridDumpComparison problems that do not generate
    # checkpoint files, but nothing will happen in that case.
    items = os.listdir(pathToRunDir)
    for item in items:
      if re.match(".*?_chk_\d+$", item):
        chkFiles.append(item)

    # sorting and reversing will put the highest-numbered
    # checkpoint file at index 0
    chkFiles.sort()
    chkFiles.reverse()

    if len(chkFiles) > 0:
      chkMax = chkFiles[0]
      self.masterDict["chkMax"] = chkMax
      for fileToDelete in filesToDelete[:]:
        if fileToDelete == chkMax:
          filesToDelete.remove(fileToDelete)

class ComparisonTester(TesterTemplate):

  def compare(self, pathToFileA, pathToFileB, cmd):
    log                = self.masterDict["log"]                # guaranteed to exist by flashTest.py
    arch               = self.masterDict["arch"]               # guaranteed to exist by flashTest.py
    outfile            = self.masterDict["outfile"]            # guaranteed to exist by flashTest.py
    pathToRunDir       = self.masterDict["pathToRunDir"]       # guaranteed to exist by flashTest.py
    pathToLocalArchive = self.masterDict["pathToLocalArchive"] # guaranteed to exist by flashTest.py

    pathToFileA = os.path.normpath(pathToFileA)
    pathToFileB = os.path.normpath(pathToFileB)

    if not os.path.isabs(pathToFileA):
      pathToFileA = os.path.join(pathToRunDir, pathToFileA)
    if not os.path.isabs(pathToFileB):
      pathToFileB = os.path.join(pathToRunDir, pathToFileB)

    if pathToFileA.startswith(pathToLocalArchive):
      try:
        arch.confirmInLocalArchive(pathToFileA)
      except Exception as e:
        log.err("%s\n" % e +
                "Aborting this test.")
        outfile.write(str(e))
        return False
    elif not os.path.isfile(pathToFileA):
      if not os.path.exists(pathToFileA):
        log.stp("\"%s\" does not exist." % pathToFileA)
        outfile.write("\"%s\" does not exist.\n" % pathToFileA)
      else:
        log.stp("\"%s\" is not a regular file." % pathToFileA)
        outfile.write("\"%s\" is not a regular file.\n" % pathToFileA)
      return False

    if pathToFileB.startswith(pathToLocalArchive):
      try:
        arch.confirmInLocalArchive(pathToFileB)
      except Exception as e:
        log.err("%s\n" % e +
                "Aborting this test.")
        outfile.write(str(e))
        return False
    elif not os.path.isfile(pathToFileB):
      if not os.path.exists(pathToFileB):
        log.stp("\"%s\" does not exist." % pathToFileB)
        outfile.write("\"%s\" does not exist.\n" % pathToFileB)
      else:
        log.stp("\"%s\" is not a regular file." % pathToFileB)
        outfile.write("\"%s\" is not a regular file.\n" % pathToFileB)
      return False

    log.stp("FileA: \"%s\"\n" % pathToFileA +
            "FileB: \"%s\""   % pathToFileB)
    outfile.write("FileA: \"%s\"\n" % pathToFileA +
                  "FileB: \"%s\"\n\n" % pathToFileB)

    outfile.write("script: %s\n" % cmd)
    return getProcessResults(cmd)


  def compareToYesterday(self, pathToFile, pathToCompareExecutable):
    yesterDate = time.strftime("%Y-%m-%d", time.localtime(time.time()-24*60*60))

    pat1 = re.compile("\/\d\d\d\d-\d\d-\d\d.*?\/")
    pathToYesterFile = pat1.sub("/%s/" % yesterDate, pathToFile)

    cmd = "%s %s %s" % (pathToCompareExecutable, pathToFile, pathToYesterFile)
    return self.compare(pathToFile, pathToYesterFile, cmd)


  def yesterFileIsSameFile(self, pathToFile):
    # Try to detect situation where the putative file from yesterday is really
    # this run's file.  This happens when the current invocation was started
    # on the previous day and passed midnight.  The simple algorithm based on
    # localtime() will then fail to locate the file from the previous run correctly. - KW
    yesterDate = time.strftime("%Y-%m-%d", time.localtime(time.time()-24*60*60))

    pat1 = re.compile("\/\d\d\d\d-\d\d-\d\d.*?\/")
    pathToYesterFile = pat1.sub("/%s/" % yesterDate, pathToFile)

    return os.path.samefile(pathToFile, pathToYesterFile)


class SfocuTester(ComparisonTester):

  def test(self):
    log          = self.masterDict["log"]           # guaranteed to exist by flashTest.py
    pathToFlash  = self.masterDict["pathToFlash"]   # guaranteed to exist by flashTest.py
    pathToRunDir = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py
    outfile      = self.masterDict["outfile"]       # guaranteed to exist by flashTest.py

    if not self.masterDict.has_key("chkMax"):
      log.stp("No checkpoint files were produced, so no comparisons can be made.")
      outfile.write("No checkpoint files were produced, so no comparisons can be made.\n")
      return False

    # else
    pathToChkMax = os.path.join(pathToRunDir, self.masterDict["chkMax"])
    pathToSfocu = self.masterDict.get("pathToSfocu", os.path.join(pathToFlash, "tools", "sfocu", "sfocu"))
    sfocuScript = self.masterDict.get("sfocuScript", pathToSfocu)

    # before comparing to the benchmark, compare to yesterday's result
    # this portion assumes that copies of the highest-numbered checkfile
    # are being retained locally in FlashTest's "output" directory
    log.stp("Part 1: Compare this invocation's result to yesterday's")
    outfile.write("Part 1: Compare this invocation's result to yesterday's\n")

    retval = self.compareToYesterday(pathToChkMax, sfocuScript)

    if retval:
      # unpack the tuple
      out, err, duration, exitStatus = retval

      # An exit status of 0 means a normal termination without errors.
      if exitStatus == 0:
        log.stp("Process exit-status reports sfocu ran successfully")
        outfile.write("<b>sfocu output:</b>\n"
                      + out.strip() + "\n\n")

        # Even if sfocu ran fine, the test might still have failed
        # if the two checkpoint files were not equivalent
        if out.strip().endswith("SUCCESS"):
          log.stp("comparison of benchmark files yielded: SUCCESS")
          # Set sameAsPrevious, but only after some additonal checking:
          # - The checkpoint we are comparing must be numbered higher than 0.
          # - Comparison against "yesterday's" checkpoint must have really
          #   been a comparison with a DIFFERENT file.
          if (self.masterDict["chkMax"][-5:-1] != "_0000") and \
             not self.yesterFileIsSameFile(pathToChkMax):
            self.masterDict["sameAsPrevious"] = True
        else:
          log.stp("comparison of benchmark files yielded: FAILURE")
          # The results of this test differed from the results of the
          # same test done during the previous invocation. We set the
          # key "changedFromPrevious" in masterDict (the value doesn't
          # matter) which is recognized by flashTest.py as a signal to
          # add a "!" to the ends of the "errors" files at the run,
          # build, and invocation levels.
          self.masterDict["changedFromPrevious"] = True
      else:
        log.stp("Process exit-status reports sfocu encountered an error")

        # record whatever we got anyway
        outfile.write("Process exit-status reports sfocu encountered an error\n" +
                      "<b>sfocu output:</b>\n" +
                      out.strip() + "\n\n")

    log.stp("Part 2: Compare this invocation's result to approved benchmark.")
    outfile.write("Part 2: Compare this invocation's result to approved benchmark.\n")

    if not self.masterDict.has_key("shortPathToBenchmark"):
      log.err("A key \"shortPathToBenchmark\", whose value is a relative path from\n" +
              "the local archive to a benchmark file against which the results of\n" +
              "this run can be compared, should be provided in your \"test.info\" file.")
      return False

    # else
    shortPathToBenchmark = self.masterDict["shortPathToBenchmark"]
    pathToLocalArchive = self.masterDict["pathToLocalArchive"]  # guaranteed to exist by flashTest.py
    pathToBenchmark = os.path.join(pathToLocalArchive, shortPathToBenchmark)

    cmdAndTols = [sfocuScript]
    if self.masterDict.has_key("errTol"):
      cmdAndTols.append("-e %s" % self.masterDict["errTol"])
    if self.masterDict.has_key("partErrTol"):
      cmdAndTols.append("-p %s" % self.masterDict["partErrTol"])

    cmd = "%s %s %s" % (" ".join(cmdAndTols), pathToChkMax, pathToBenchmark)
    retval = self.compare(pathToChkMax, pathToBenchmark, cmd)

    if not retval:
      return False

    # else unpack the tuple
    out, err, duration, exitStatus = retval

    # An exit status of 0 means a normal termination without errors.
    if exitStatus == 0:
      log.stp("Process exit-status reports sfocu ran successfully.")
      outfile.write("<b>sfocu output:</b>\n"
                    + out.strip() + "\n\n")

      # Even if sfocu ran fine, the test might still have failed
      # if the two checkpoint files were not equivalent
      if out.strip().endswith("SUCCESS"):
        log.stp("comparison of benchmark files yielded: SUCCESS")
        return True
      else:
        log.stp("comparison of benchmark files yielded: FAILURE")
        return False
    else:
      log.stp("Process exit-status reports sfocu encountered an error")

      # record whatever we got anyway
      outfile.write("Process exit-status reports sfocu encountered an error\n" +
                    "<b>sfocu output:</b>\n" +
                    out.strip() + "\n\n")
      # sfocu had an error, so we return false:
      return False

    return True


class GridDumpTester(ComparisonTester):
  def findDumpFiles(self):
    pathToRunDir = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py

    dumpFiles = []
    items = os.listdir(pathToRunDir)
    for item in items:
      if re.match("^FL\d+$", item):
        dumpFiles.append(item)

    return dumpFiles

  def test(self):
    log          = self.masterDict["log"]           # guaranteed to exist by flashTest.py
    pathToFlash  = self.masterDict["pathToFlash"]   # guaranteed to exist by flashTest.py
    pathToRunDir = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py
    outfile      = self.masterDict["outfile"]       # guaranteed to exist by flashTest.py

    pathToGridDumpCompare = self.masterDict.get("pathToGridDumpCompare",
                                                os.path.join(pathToFlash, "tools", "GridDumpCompare.py"))
    if not os.path.isfile(pathToGridDumpCompare):
      log.err("\"%s\" does not exist or is not a regular file.\n" % pathToGridDumpCompare +
              "Result of test: FAILURE")
      outfile.write("\"%s\" does not exist or is not a regular file.\n" % pathToGridDumpCompare +
                    "Result of test: FAILURE\n")
      return False

    # else
    dumpFiles = self.findDumpFiles()

    if len(dumpFiles) == 0:
      log.err("No GridDump files were found, so no comparison can be made." +
              "Result of test: FAILURE")
      outfile.write("No GridDump files were found, so no comparison can be made.\n" +
                    "Result of test: FAILURE\n")
      return False

    # else
    log.stp("Part 1: Compare this invocation's results to yesterday's")
    outfile.write("Part 1: Compare this invocation's results to yesterday's\n")

    for dumpFile in dumpFiles:
      pathToDumpFile = os.path.join(pathToRunDir, dumpFile)

      retval = self.compareToYesterday(pathToDumpFile, pathToGridDumpCompare)

      if retval:
        # unpack the tuple
        out, err, duration, exitStatus = retval

        if exitStatus == 0:
          log.stp("comparison of dump-files yielded: SUCCESS")
        elif exitStatus == 1:
          log.stp("comparison of dump-files yielded: FAILURE")
          # The results of this test differed from the results of the
          # same test done during the previous invocation. We set the
          # key "changedFromPrevious" in masterDict (the value doesn't
          # matter) which is recognized by flashTest.py as a signal to
          # add a "!" to the ends of the "errors" files at the run,
          # build, and invocation levels.
          self.masterDict["changedFromPrevious"] = True
        else:
          log.stp("Process exit-status reports GridDumpCompare.py encountered an error")

        # record whatever we got in all cases
        outfile.write("<b>GridDumpCompare.py output:</b>\n" +
                      out.strip() + "\n\n")

    log.stp("Part 2: Compare this invocation's result to approved benchmark.")
    outfile.write("Part 2: Compare this invocation's result to approved benchmark.\n")

    if not self.masterDict.has_key("shortPathToBenchmarkDir"):
      log.err("A key \"shortPathToBenchmarkDir\", whose value is a relative path from the\n" +
              "local archive to the directory containing the files against which the results\n" +
              "of this run can be compared, should be provided in your \"test.info\" file.")
      return False

    # else
    # For GridDump comparisons we bring over a whole directory from the archive
    # which contains all dumps made for a single run (each dump encapsulates the
    # values of a single variable at different points on the grid).
    # This is different from sfocu comparisons, where we only bring over a single
    # file, the highest-numbered checkpoint file.
    shortPathToBenchmarkDir = self.masterDict["shortPathToBenchmarkDir"]

    arch = self.masterDict["arch"]  # guaranteed to exist by flashTest.py
    try:
      arch.confirmInLocalArchive(shortPathToBenchmarkDir)
    except Exception as e:
      log.err("%s\n" % e +
              "Aborting this test.")
      outfile.write(str(e))
      return False

    # else all files have been successfully brought over from
    # the remote archive into the local archive
    pathToLocalArchive = self.masterDict["pathToLocalArchive"]  # guaranteed to exist by flashTest.py

    allPassed = True

    for dumpFile in dumpFiles:
      pathToDumpFile = os.path.join(pathToRunDir, dumpFile)
      pathToBenchmark = os.path.join(pathToLocalArchive, shortPathToBenchmarkDir, dumpFile)

      cmd = "%s %s %s" % (pathToGridDumpCompare, pathToDumpFile, pathToBenchmark)
      retval = self.compare(pathToDumpFile, pathToBenchmark, cmd)

      if not retval:
        allPassed = False
        continue

      # else unpack the tuple
      out, err, duration, exitStatus = retval

      if exitStatus == 0:
        log.stp("comparison of dump-files yielded: SUCCESS")
      elif exitStatus == 1:
        log.stp("comparison of dump-files yielded: FAILURE")
        allPassed = False
      else:
        log.stp("Process exit-status reports GridDumpCompare.py encountered an error")
        allPassed = False

      # record whatever we got in all cases
      outfile.write("<b>GridDumpCompare.py output:</b>\n" +
                    out.strip() + "\n\n")

    return allPassed


class UnitTester(TesterTemplate):
  """
  Implements a test method for all Flash unit-tests that follow the accepted
  unit-test standard. This standard prescribes that a unit-test will produce
  files named:

    unitTest_0, unitTest_1, ..., unitTest_n

  where 'n' is the number of processors on which the test ran. If the unit-
  test was completely successful, each of these files will contain the text:

    "all results conformed with expected values."

  Otherwise they will contain information describing why the test failed.

  This test method reads files whose names match those described above and
  determines success or failure based on the presence or absence therein of
  the aforementioned success string.
  """
  def test(self):
    log          = self.masterDict["log"]           # guaranteed to exist by flashTest.py
    pathToFlash  = self.masterDict["pathToFlash"]   # guaranteed to exist by flashTest.py
    pathToRunDir = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py
    outfile      = self.masterDict["outfile"]       # guaranteed to exist by flashTest.py

    UGPat = re.compile("^unitTest_\d+$")

    files = os.listdir(pathToRunDir)
    files = [f for f in files if UGPat.search(f)]  # only want files
                                                   # matching 'UGPat'

    if len(files) > 0:
      success = True
      successStr = "all results conformed with expected values."
      # put in alphabetical order
      files.sort()
      for f in files:
        text =  "<i>reading file %s:</i>" % f
        text += "<div style='margin-left:10px;'>"
        fileText = open(os.path.join(pathToRunDir, f), "r").read().lower()
        if fileText.count(successStr) == 0:
          success = False
        text += fileText
        text += "</div>"
        outfile.write(text)
    else:
      success = False

    if success:
      log.stp("result of test: SUCCESS")
    else:
      log.stp("result of test: FAILURE")

    return success


class DefaultSetupper(FlashSetupper):
  def setup(self):
    """
    The Default test by definition sets up the problem called "Default"
    This test doesn't use a "test.info" file, so we override the setup
    method long enough to set some key values in 'masterDict', then
    revert back to the setup method of UniversalTemplate.
    """
    self.masterDict["setupName"] = "Default"
    self.masterDict["setupOptions"] = "-site=%s -auto" % self.masterDict["flashSite"]

    return FlashSetupper.setup(self)

class SiteSetupper(FlashSetupper):
  def setup(self):
    """
    This setupper differs from the normal behavior only by prepending
    " -site=<flashSite>" to the setupOptions and thus to the command line for the
    setup call.
    """
    if self.masterDict.get("flashSite",""):
      setupOptions   = self.masterDict.get("setupOptions","")
      self.masterDict["setupOptions"] = "-site=%s %s" % (self.masterDict["flashSite"], setupOptions)

    return FlashSetupper.setup(self)

class IntelSetupper(SiteSetupper):
  def setup(self):
    """
    This setupper differs from the SiteSettuper only by prepending
    " -makefile=Intel" to the setupOptions and thus to the command line for the
    setup call.
    """
    setupOptions   = self.masterDict.get("setupOptions","")
    self.masterDict["setupOptions"] = "-makefile=Intel %s" % setupOptions

    return SiteSetupper.setup(self)

class DebugSetupper(FlashSetupper):
  def setup(self):
    """
    This setupper differs from the normal behavior only by appending
    " -debug" to the setupOptions and thus to the command line for the
    setup call.
    """
    setupOptions   = self.masterDict.get("setupOptions","")
    self.masterDict["setupOptions"] = "%s -debug" % setupOptions
    self.masterDict["usingDebugSetupper"] = True

    return FlashSetupper.setup(self)

class LibmodeSetupper(FlashSetupper):
  def setup(self):
    """
    This setupper differs from the normal behavior only by appending
    " ParameshLibraryMode=True" to the setupOptions and thus to the command line
    for the setup call.
    """
    setupOptions   = self.masterDict.get("setupOptions","")
    self.masterDict["setupOptions"] = "%s ParameshLibraryMode=True" % setupOptions

    return FlashSetupper.setup(self)

class NoClobberSetupper(SiteSetupper):
  def setup(self):
    """
    This setupper differs from the SiteSetupper only by appending
    " -noclobber" to the setupOptions and thus to the command line for the
    setup call.
    """
    setupOptions   = self.masterDict.get("setupOptions","")
    self.masterDict["setupOptions"] = "%s -noclobber" % setupOptions

    return SiteSetupper.setup(self)

class StaticHyArraysSetupper(NoClobberSetupper):
  def setup(self):
    """
    This setupper differs from the SiteSetupper only by appending
    " -noclobber" to the setupOptions and thus to the command line for the
    setup call.
    """
    setupOptions   = self.masterDict.get("setupOptions","")
    self.masterDict["setupOptions"] = "%s StaticHyArrays=True" % setupOptions

    return NoClobberSetupper.setup(self)


class RestartExecuter(ComparisonExecuter):
  """
  This class subclasses ComparisonExecuter instead of FlashExecuter
  so that the former's "adjustFilesToDelete()" method, which sets a
  value for "checkMax" will be called.
  """
  def execute(self):
    """
    The Restart test first runs a simulation in the normal way, generating
    a few checkpoint files. It then takes a checkpoint file from the middle
    of the run (as specified in the "test.info" data) and runs the problem
    again, this time restarting from the checkpoint. If the end-checkpoint
    file from the restart-run matches the end-checkpoint file from the first
    run, the test is considered a success
    """
    log          = self.masterDict["log"]           # guaranteed to exist by flashTest.py
    pathToRunDir = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py

    pathToPart1Parfile  = self.masterDict["part1Parfile"]   # supposed to exist in "test.info"
    part1NumProcs       = self.masterDict["part1NumProcs"]  # supposed to exist in "test.info"
    benchmark1          = self.masterDict["benchmark1"]     # supposed to exist in "test.info"
    benchmark2          = self.masterDict["benchmark2"]     # supposed to exist in "test.info"
    pathToExeScript = self.masterDict["pathToExeScript"]  # guaranteed to exist by flashTest.py

    # First run the simulation through to generate
    # benchmarks 1 and 2 in the normal way
    pathToFlashTest = self.masterDict["pathToFlashTest"]  # guaranteed to exist by flashTest.py

    # read the execution script from "exeScript"
    exeScriptFile = os.path.join(pathToFlashTest, pathToExeScript)
    if not os.path.isfile(exeScriptFile):
      log.err("File \"exeScript\" not found. Unable to run executable.\n" +
              "Skipping all runs.")
      return False

    # else

    # hackily substitute into masterDict's "parfile" keyword the
    # name of the parfile we need to run this whole simulation
    # *without* a restart so it will in turn be substituted into
    # masterDict["script"] below.
    part1Parfile                = os.path.basename(pathToPart1Parfile)
    part2Parfile                = self.masterDict["parfile"]
    part2NumProcs               = self.masterDict["numProcs"]
    self.masterDict["parfile"]  = part1Parfile
    self.masterDict["numProcs"] = part1NumProcs

    lines = open(exeScriptFile).read().split("\n")
    lines = [line.strip() for line in lines
             if len(line.strip()) > 0 and not line.strip().startswith("#")]
    script = "\n".join(lines)
    self.masterDict["script"] = script
    script = self.masterDict["script"]  # do it this way so that any angle-bracket variables
                                        # in "exeScript" will be filled in by self.masterDict

    log.stp("Generating seed-benchmark \"%s\"\n" % benchmark1 +
            "and comparison-benchmark \"%s\"\n" % benchmark2 +
            "with parfile \"%s\" and numProcs=%s" % (part1Parfile, part1NumProcs))

    # write part1 parfile into 'runDir'
    parfileText = open(pathToPart1Parfile).read()
    open(os.path.join(pathToRunDir, part1Parfile), "w").write(parfileText)

    # cd to output directory to run executable
    os.chdir(pathToRunDir)

    # get stdout/stderr and duration of execution
    out, err, duration, exitStatus = getProcessResults(script)

    flashOutput = "Results of generation of seed and comparison checkpoint files:\n"
    flashOutput += (out + "\n")
    flashOutput += (("*" * 80) + "\n")
    _write_to_file(os.path.join(pathToRunDir, "flash_output"), "w",
                   flashOutput,
                   errors="ignore",
    )

    if len(err) > 0:
      flashError = "Error in generation of seed and comparison checkpoint files:\n"
      flashError += (err + "\n")
      flashError += (("*" * 80) + "\n")
      _write_to_file(os.path.join(pathToRunDir, "flash_error"), "w",
                     flashError,
                     errors="backslashreplace",
      )

    # An exit status of 0 means a normal termination without errors.
    if exitStatus == 0:
      log.stp("Process exit-status reports execution successful")
    else:
      log.stp("Process exit-status reports execution failed.")
      pathToFlashExe = self.masterDict["pathToFlashExe"]  # set by FlashCompiler, above
      if len(pathToFlashExe) > 0 and pathToFlashExe[0] == '/':
        time.sleep(1)
        killallCmd = 'killall -v -HUP %s' % pathToFlashExe
#        log.stp('killallCmd is "%s"' % killallCmd)
        p = subprocess.Popen([killallCmd],shell=True,stderr=subprocess.PIPE,close_fds=True)
        killStatus = p.wait()
        if killStatus==0:
          out = p.stderr.read().strip()
          if len(out) > 0:
            log.stp(killallCmd)
            log.info(out)
#        else:
#          log.stp("Exit status %d from %s" % (killStatus, killallCmd))
      else:
        log.stp('pathToFlashExe is "%s"' % pathToFlashExe)
      return False

    # search the parfile output directory for the
    # seed-checkpoint and comparison-checkpoint files
    items = os.listdir(pathToRunDir)
    for item in items:
      if item == benchmark1:
        # this will be the seed-checkpoint file
        break  # skip "else" clause below
    else:
      log.stp("Expected seed-checkpoint file \"%s\" was not generated.\n" % benchmark1 +
              "Skipping all runs.")
      return False

    # search the parfile output directory for the comparison checkpoint file
    for item in items:
      if item == benchmark2:
        # This will be the comparison-checkpoint file.
        # Rename it so it won't get overwritten in part2.
        os.rename(item, item + "_orig")
        break  # skip "else" clause below
    else:
      log.stp("Expected comparison checkpoint file \"%s\" was not generated.\n" % benchmark2 +
              "Skipping all runs.")
      return False

    # cd back to flashTest
    os.chdir(pathToFlashTest)

    # We've now guaranteed that the "seed" checkpoint file is in
    # place in 'runDir', so reset the parfile and numProcs values
    # and call the parent class's executer
    self.masterDict["parfile"]  = part2Parfile
    self.masterDict["numProcs"] = part2NumProcs
    return ComparisonExecuter.execute(self)


class RestartTester(ComparisonTester):
  def test(self):
    log                = self.masterDict["log"]           # guaranteed to exist by flashTest.py
    pathToFlash        = self.masterDict["pathToFlash"]   # guaranteed to exist by flashTest.py
    pathToRunDir       = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py
    outfile            = self.masterDict["outfile"]       # guaranteed to exist by flashTest.py

    benchmark1 = self.masterDict["benchmark1"]  # supposed to exist in "test.info"
    benchmark2 = self.masterDict["benchmark2"]  # supposed to exist in "test.info"

    pathToSfocu = self.masterDict.get("pathToSfocu", os.path.join(pathToFlash, "tools", "sfocu", "sfocu"))
    sfocuScript = self.masterDict.get("sfocuScript", pathToSfocu)

    chkMax = self.masterDict["chkMax"]  # should always have a value because even if execution produced
                                        # no checkpoint files, the seed-checkpoint copied into 'runDir'
                                        # should have been tagged as "chkMax" in ComparisonExecuter's
                                        # "adjustFilesToDelete" method.

    if chkMax == benchmark1:
      log.stp("No additional checkpoint files were produced after the restart.\n" +
              "No comparison can be made.")
      return False

    # else
    pathToChkMax = os.path.join(pathToRunDir, chkMax)
    pathToBenchmark2 = os.path.join(pathToRunDir, (benchmark2 + "_orig"))

    cmdAndOpts = [sfocuScript]
    if "errTol" in self.masterDict:
      cmdAndOpts.append("-e %s" % self.masterDict["errTol"])
    if "partErrTol" in self.masterDict:
      cmdAndOpts.append("-p %s" % self.masterDict["partErrTol"])
    if "sfocuFlags" in self.masterDict:
      compFlags = ""
      compFlags = self.masterDict["sfocuFlags"]
      cmdAndOpts.append(compFlags)

    cmd = "%s %s %s" % (" ".join(cmdAndOpts), pathToChkMax, pathToBenchmark2)
    retval = self.compare(pathToChkMax, pathToBenchmark2, cmd)

    if not retval:
      log.stp("Error processing command \"%s\"\n" % cmd)
      return False

    # else unpack the tuple
    out, err, duration, exitStatus = retval

    # An exit status of 0 means a normal termination without errors.
    if exitStatus == 0:
      log.stp("Process exit-status reports sfocu ran successfully.")
      outfile.write("<b>sfocu output:</b>\n"
                    + out.strip() + "\n\n")

      # Even if sfocu ran fine, the test might still have failed
      # if the two checkpoint files were not equivalent
      if out.strip().endswith("SUCCESS"):
        log.stp("comparison of benchmark files yielded: SUCCESS")
        return True
      else:
        log.stp("comparison of benchmark files yielded: FAILURE")
        return False
    else:
      log.stp("Process exit-status reports sfocu encountered an error")

      # record whatever we got anyway
      outfile.write("Process exit-status reports sfocu encountered an error\n" +
                    "<b>sfocu output:</b>\n" +
                    out.strip() + "\n\n")
      # sfocu had an error, so we return false:
      return False

    return True


class CompositeExecuter(FlashExecuter):
  def __init__ (self, testObject):
    """
    Override the template's method to allow us to correctly handle restarts.
    """
    self.owner = testObject
    self.masterDict = testObject.masterDict

    self.restartParfiles = None
    self.parfilesLeft = True

  def adjustFilesToDelete(self, filesToDelete):
    """
    Notes the comparison benchmark.  Only removes from to delete list if sfocu
    comparison has not changed.  This value is also used for the sfocu compariosn.
    Make sure called afer comparison.
    """
    #comparisonFile = os.path.basename(self.masterDict["comparisonBenchmark"])
    #restartFile = os.path.basename(self.masterDict["restartBenchmark"])
    checkpointBasename = self.masterDict["checkpointBasename"]
    comparisonFile = checkpointBasename + self.masterDict["comparisonNumber"]
    restartFile = checkpointBasename + self.masterDict["restartNumber"]

    #Populate the chkMax so we can determine if the restart test actually ran.
    pathToRunDir = self.masterDict["pathToRunDir"] #flashTest.py has this
    chkFiles = []

    files = os.listdir(pathToRunDir)
    for file in files:
      if re.match(".*?_chk_\d+$", file):
        chkFiles.append(file)

    chkFiles.sort()
    chkFiles.reverse()
    #this is the furthest file we've gotten on this run
    if len(chkFiles) > 0:
      chkMax = chkFiles[0]
      self.masterDict["chkMax"] = chkMax

#    for chkFile in chkFiles:
#       filesToDelete.append(chkFile)

    #get plot and part files?

    #DEV: have to make sure comparitor is smart enough to actually figure this out.
    #Assume that we are keeping the file, can add back in later?
    #DEV: Just Keep Them for now.
    pahToRunDir = self.masterDict["pathToRunDir"]

    for fileToDelete in filesToDelete[:]:
      if fileToDelete == restartFile:
        filesToDelete.remove(fileToDelete)
      elif fileToDelete == comparisonFile:
        filesToDelete.remove(fileToDelete)

    return

  def execute(self):
    """
    Overridden to allow both Comparison and restart behaviors
    """
    log             = self.masterDict["log"]              # guaranteed to exist by flashTest.py
    pathToFlash     = self.masterDict["pathToFlash"]      # guaranteed to exist by flashTest.py
    pathToRunDir    = self.masterDict["pathToRunDir"]     # guaranteed to exist by flashTest.py
    pathToFlashTest = self.masterDict["pathToFlashTest"]  # guaranteed to exist by flashTest.py
    pathToExeScript = self.masterDict["pathToExeScript"]  # guaranteed to exist by flashTest.py

    #DEV:Make sure these are safe.
    comparisonParfile = self.masterDict["parfile"]    #new for this mode

    #Since we are restarting we have to run twice, with different parfiles.
    #This is called once for each parfile entry in a multi-parfile run, so this
    #will only iterate twice per exectuion.

    #populate the restart parfiles, if we don't have them. Head will be next to use.
    if self.restartParfiles is None:
      restartParfileNames = self.masterDict["restartParfiles"] #new for this mode: parfile for restarts
      self.restartParfiles = restartParfileNames.split(None)
      #sanity check.  Specification is that the number of entries in parfiles and restartParfiles is the same.
      if len(self.restartParfiles) != len(self.masterDict["parfiles"]):
        log.err("Mismatch in number of entries in parfiles and restartParfiles entries for test.")
        return False

    else:
      if type(self.restartParfiles) == type('abc'):
        self.restartParfiles= self.restartParfiles.split(None)

    restartParfile = self.restartParfiles[0]
    del self.restartParfiles[0]
    if len(self.restartParfiles) == 0:
      self.restartParfiles = None
  ######################################################
    iteration = 0
    #loop, requires three iterations:
    while(iteration < 3):
      #make sure that the parfile has correct path.
      if iteration == 0:
        if "restartBenchmark" in self.masterDict or restartParfile == "none":
          iteration += 1
          continue # skip iteration
        else: # must verify transparency restart for auto approved restart benchmark
          log.stp("restartBenchmark not present, performing long-run to verify transparent restart.\n")
          def readpar(path):
            f = open(path, "r")
            parms = dict(
                [[m.group(1).lower(), m.group(2)]
                 for m in
                     [re.match("\s*(\w+)\s*=\s*(\S|\S.*\S)\s*$", line)
                      for line in f.readlines()]
                 if m
                 ]
            )
            f.close()
            return parms
          def writepar(path, parms):
            f = open(path, "w")
            f.writelines(["%s = %s\n" % (k,v) for k,v in parms.items() ])
            f.close()
          pathToCompParfile = os.path.join(pathToRunDir, comparisonParfile)
          pathToRestParfile = os.path.join(pathToRunDir, restartParfile)
          parComp = readpar(pathToCompParfile)
          parRest = readpar(pathToRestParfile)
          if "nend" in parRest: parComp["nend"] = parRest["nend"]
          if "tmax" in parRest: parComp["tmax"] = parRest["tmax"]
          if "dr_shortenlaststepbeforetmax" in parRest: parComp["dr_shortenlaststepbeforetmax"] = parRest["dr_shortenlaststepbeforetmax"]
          pathToParfile = os.path.join(pathToRunDir, "restart_longrun_hyn7rt0v20.par")
          writepar(pathToParfile, parComp)
      elif iteration == 1:
        pathToParfile = comparisonParfile
      #we have to swap parfiles.  If none, note this fact.
      #if the none placeholder is used, stamp a message, not an
      #error.  This is intentional.
      elif iteration == 2:
        pathToParfile = restartParfile

        #This is neither a failure nor a success.
        if(pathToParfile == "none"):
          log.stp("Parfile specified as none for this test.")
          return runSucceeded

        if not runSucceeded:
          break
      #the masterDict entry is the parfile that will be used.
      parfileName = os.path.basename(pathToParfile)
      self.masterDict["parfile"] = parfileName

      # read the execution script from "exeScript"
      exeScriptFile = os.path.join(pathToFlashTest, pathToExeScript)
      if not os.path.isfile(exeScriptFile):
        log.err("File \"exeScript\" not found. Unable to run executable.\n" +
                "Skipping all runs.")
        return False


      lines = open(exeScriptFile).read().split("\n")
      lines = [line.strip() for line in lines
               if len(line.strip()) > 0 and not line.strip().startswith("#")]
      script = "\n".join(lines)
      self.masterDict["script"] = script
      script = self.masterDict["script"]  # do it this way so that any angle-bracket variables
                                        # in "exeScript" will be filled in by self.masterDict
      # determine 'pathToRunSummary'
      pathToRunSummary = os.path.join(pathToRunDir, "run_summary")

      # cd to output directory to run executable
      os.chdir(pathToRunDir)

      #plant the parfiles needed in the execution directory
      parfileText = open(pathToParfile).read()
      open(os.path.join(pathToRunDir, parfileName), 'w').write(parfileText)

      # obtain and record number of processors
      if not self.masterDict.has_key("numProcs"):
        self.masterDict["numProcs"] = 1
      open(pathToRunSummary,"a").write("numProcs: %s\n" % self.masterDict["numProcs"])

      # record mpirun invocation in "flash_call" file and in log
      open(os.path.join(pathToRunDir, "flash_call"), "w").write(script)
      log.stp(script)

      # get stdout/stderr and duration of execution and write to file
      out, err, duration, exitStatus = getProcessResults(script)

      open(os.path.join(pathToRunDir, "flash_output"),"a").write(out)
      if len(err) > 0:
        open(os.path.join(pathToRunDir, "flash_error"),"a").write(err)

      # record execution time in the run summary and logfile in human-readable form
      duration = secondsToHuman.convert(duration)
      open(pathToRunSummary,"a").write("wallClockTime: %s\n" % duration)
      log.info("duration of execution: %s" % duration)

      # search the parfile output directory for checkpoint files
      checkFiles = [f for f in os.listdir(pathToRunDir) if re.match(".*?_chk_\d+$", f)]

      # record number and names of checkpoint files in the run summary
      open(pathToRunSummary,"a").write("numCheckfiles: %s\n" % len(checkFiles))
      for checkFile in checkFiles:
        open(pathToRunSummary,"a").write("checkFile: %s\n" % checkFile)

      if iteration == 0:
        #this was a full run for restart transparency test, save final checkpoint delete all others
        if len(checkFiles) > 0:
          checkFiles.sort()
          os.rename(checkFiles.pop(), os.path.join(pathToRunDir, "chk_restart_longrun_9f402yfg"))
          for chk in checkFiles: os.remove(chk)
        else:
          log.stp("Long run did not produce expected checkpoints")
          if exitStatus == 0:
            log.stp(" - marking exit-status as failed")
            exitStatus = 3

      # An exit status of 0 means a normal termination without errors.
      if exitStatus == 0:
        log.stp("Process exit-status reports execution successful")
        runSucceeded = True
      else:
        log.stp("Process exit-status reports execution failed")
        pathToFlashExe = self.masterDict["pathToFlashExe"]  # set by FlashCompiler, above
        if len(pathToFlashExe) > 0 and pathToFlashExe[0] == '/':
          time.sleep(1)
          killallCmd = 'killall -v -HUP %s' % pathToFlashExe
#          log.stp('killallCmd is "%s"' % killallCmd)
          p = subprocess.Popen([killallCmd],shell=True,stderr=subprocess.PIPE,close_fds=True)
          killStatus = p.wait()
          if killStatus==0:
            out = p.stderr.read().strip()
            if len(out) > 0:
              log.stp(killallCmd)
              log.info(out)
#          else:
#            log.stp("Exit status %d from %s" % (killStatus, killallCmd))
        else:
          log.stp('pathToFlashExe is "%s"' % pathToFlashExe)
        runSucceeded = False
      # iteration loop
      iteration += 1

    # cd back to flashTest
    os.chdir(pathToFlashTest)

    return runSucceeded


#This is going to need an external file to keep last completed run.
#Use pre-existing sfocu machinery
class CompositeTester(ComparisonTester):

#   Def __init__(Self, Testobject):
#     """
#     We Must Check For A List Of Last Completed Comparison Tests, Hence
#     The Initialization Method Of The Composite Case Tester Needs
#     To Be Overridden To Check For This File.
#     """

#     Self.Owner = Testobject
#     Self.Masterdict = Testobject.Masterdict

     #Open A File In The Top Level Of The Flash Test Directory.
     #If Not There, Set A Sentinel For The Filename (Null)
#     Lastchangedfile = Open("Last_changed_checkpoint", 'R+')
#     For Lines In Lastchangedfile:



  def compareFiles(self, pathToFile1, pathToFile2, compOptions, compareYesterday=False):
    #return true if test is successful.  Return false if we encounter an error.

    #Let's break this out for readability sake.
    log = self.masterDict["log"] #from flashTest.py
    outfile = self.masterDict["outfile"] #from flashTest.py

    if not os.path.exists(pathToFile1):
      log.stp("\"%s\" does not exist." % pathToFile1)
      outfile.write("\"%s\" does not exist.\n" % pathToFile1)
      return False

    #pathToLocalArchive = self.masterDict["pathToLocalArchive"] #belongs to flashTest.py
    #pathToFile = os.path.join(pathToLocalArchive, shortPathToFile)
    pathToFlash = self.masterDict["pathToFlash"] #from flashTest.py

    pathToSfocu = self.masterDict.get("pathToSfocu", os.path.join(pathToFlash, "tools", "sfocu", "sfocu"))
    sfocuScript = self.masterDict.get("sfocuScript", pathToSfocu)

    cmdAndArgs = [sfocuScript]
    cmdAndArgs.append(compOptions)
    #presently only supporting tolerances should we allow for arbitrary flags?
    #if self.masterDict.has_key("sfocuFlags"):
     # cmdAndArgs.append.("%s" % self.masterDict["sfocuFlags"])

    if compareYesterday == False:
      if "errTol" in self.masterDict :
        cmdAndArgs.append("-e %s " % self.masterDict["errTol"])
      if "partErrTol" in self.masterDict :
        cmdAndArgs.append("-p %s " % self.masterDict["partErrTol"])

    locFile2 = pullfile(pathToFile2,log)
    if not locFile2:
      return False #something seriously failed with pullfile.

    cmd = "%s %s %s" % (" ".join(cmdAndArgs), pathToFile1, locFile2)
    #log.stp('SFOCU CMD: ' + cmd)
    #outfile.write('SFOCU CMD: ' + cmd)
    retval = self.compare(pathToFile1, locFile2, cmd)
    pushfile(pathToFile2)

    if not retval:
      return False #something catastrophically failed with sfocu.

    out, err, duration, exitStatus = retval

    if exitStatus == 0:
      log.stp("Process exit-status reports sfocu ran successfully.")
      outfile.write("<b>sfocu output:</b>\n" + out.strip() + "\n\n")

      if out.strip().endswith("SUCCESS"):
        log.stp("comparison of benchmark files yielded: SUCCESS")
        return True
      else:
        log.stp("comparison of benchmark files yielded: FAILURE")
        return False
    else:
      log.stp("Process exit-status reports sfocu encountered an error")
      #record what we got before the error.
      outfile.write("Process exit-status retports sfocu encountered an error\n" +
                    "<b>sfocu output:</b>\n" + out.strip() + "\n\n")
      return False
    return True

  def adjustFilesToDelete(self, checkpointChanged, restartChanged):

    """
    We can take files that we want to keep out of the files to delete file with
    this.  This file is written by the executer.
    """

    pathToRunDir = self.masterDict["pathToRunDir"]  #guaranteed to exist by flashTest.py
    checkpointFilename = None
    if checkpointChanged:
      filesToDelete = []


 #   deleteFile = open(os.path.join(pathToRunDir, "files_to_delete"), "r")

    #find the line to remove and do not include it
   # for line in deleteFile:
   #   if line == checkpointFilename:
   #     pass
   #   elif line == restartFilename:
   #     pass
   #   else:
   #     filesToDelete.append(line)

   #deleteFile.close()

   # open(os.path.join(pathToRunDir, "files_to_delete"), 'w').write("\n".join(filesToDelete))

    return

  def test(self):
    log                = self.masterDict["log"]           # guaranteed to exist by flashTest.py
    pathToFlash        = self.masterDict["pathToFlash"]   # guaranteed to exist by flashTest.py
    pathToRunDir       = self.masterDict["pathToRunDir"]  # guaranteed to exist by flashTest.py
    outfile            = self.masterDict["outfile"]       # guaranteed to exist by flashTest.py

    restartBenchmark = self.masterDict.get("restartBenchmark","")  # supposed to exist in "test.info"

    pathToSfocu = self.masterDict.get("pathToSfocu", os.path.join(pathToFlash, "tools", "sfocu", "sfocu"))
    sfocuScript = self.masterDict.get("sfocuScript", pathToSfocu)

    if "chkMax" not in self.masterDict:
      log.stp("No checkpoint files were produced, so no comparisons can be made.")
      outfile.write("No checkpoint files were produced, so no comparisons can be made.")
      return False
    else:
      chkMax = self.masterDict["chkMax"]  # should always have a value because even if execution produced
                                        # no checkpoint files, the seed-checkpoint copied into 'runDir'
                                        # should have been tagged as "chkMax" in ComparisonExecuter's
                                        # "adjustFilesToDelete" method.


    pathToChkMax = os.path.join(pathToRunDir, self.masterDict["chkMax"])

    #first, we do the last changed comparison. Located in localArchive/platform/test_name/test_par
    #Date of last changed in benchmark itself.  Append a file with changed on date.
    log.stp("Part 1: Compare this invocation's result to the last changed result.\n")
    outfile.write("Part 1: Compare this invocation's result to the last changed result.\n")

    #we have to make sure that the lastChanged file is

    #construct names
    targetFilename = self.masterDict["checkpointBasename"]
    targetFilename += self.masterDict["comparisonNumber"]
    pathToLocalArchive = self.masterDict["pathToLocalArchive"]
    pathToRunDir  =  self.masterDict["pathToRunDir"]
    pathToRunFile = os.path.join(pathToRunDir, targetFilename)

    siteDir = self.masterDict["siteDir"]
    buildDir = self.masterDict["buildDir"]
    runDir = self.masterDict["runDir"]

    pathToLastChanged = os.path.join(pathToLocalArchive, siteDir, buildDir, runDir, targetFilename)

    #ensure that the lastChanged file exists, if not, then we cannot run this comparison.
    if not os.path.isfile(pathToLastChanged):
      retval1 = False
      log.stp("ERROR: Unable to compare to the last changed checkpoint:\n %s not found.\n" % pathToLastChanged)
      outfile.write("ERROR: Unable to compare to the last changed checkpoint:\n %s not found.\n" % pathToLastChanged)
    else:
      pathToLastChangedDates = os.path.join(pathToLocalArchive, siteDir, buildDir, runDir, "lastChangedDates")
      out, err, duration, exitStatus = getProcessResults("tail -1 %s" % pathToLastChangedDates, 5, False)
      if (exitStatus == 0):
        log.stp("Last changed result is from %s.\n" % out.strip())
        outfile.write("Last changed result is from %s.\n" % out.strip())
      compFlags = " "
      if "sfocuFlags" in self.masterDict:
        compFlags = self.masterDict["sfocuFlags"]

      retval1 = self.compareFiles(pathToRunFile, pathToLastChanged, compFlags, compareYesterday=True)

    #self.masterDict["changedFromPrevious"] = False
    #no change, we can go on normally otherwise...
    #result changed! We have to do some movement and updating.  Unless this is a debug run.
    if retval1:
        self.masterDict["sameAsPrevious"] = True
    elif "usingDebugSetupper" in self.masterDict: #if a special debug run, should not archive
        self.masterDict["changedFromPrevious"] = True
    elif not os.path.exists(pathToRunFile):
        log.stp("not attempting to copy \"%s\".\n" % pathToRunFile)
        if os.path.isfile(pathToLastChanged):
          self.masterDict["changedFromPrevious"] = True
    else:
      #If this is the first time this test has been run, we need to generate
      #our supporting directories.
      if not os.path.isdir(os.path.join(pathToLocalArchive, siteDir,buildDir, runDir)):
        if not os.path.isdir(os.path.join(pathToLocalArchive, siteDir)):
          os.mkdir(os.path.join(pathToLocalArchive, siteDir))
        if not os.path.isdir(os.path.join(pathToLocalArchive, siteDir, buildDir)):
          os.mkdir(os.path.join(pathToLocalArchive, siteDir, buildDir))
        if not os.path.isdir(os.path.join(pathToLocalArchive, siteDir,buildDir, runDir)):
          os.mkdir(os.path.join(pathToLocalArchive, siteDir,buildDir, runDir))
      try:
        pathToLastChangedDates = os.path.join(pathToLocalArchive, siteDir, buildDir, runDir, "lastChangedDates")
        lastChangedDateFile = open(pathToLastChangedDates, 'a')

        log.stp("\nattempting copy\n")
        shutil.copy(pathToRunFile, pathToLastChanged)
        log.stp("copy good\n")
        #update the date of the file.
        lastChangedDateFile.write("%s\n" % self.masterDict["dateStr"]) #datetime.date.today())

        lastChangedDateFile.close()

        #set changedFromPrevious to let flashTest.py know that this has occured

        self.masterDict["changedFromPrevious"] = True
        log.stp("Today's run moved to the last changed benchmark.\n")
        outfile.write("Today's run moved to the last changed benchmark.\n")

      except IOError:
        log.err("Cannot open the last changed date file. File move aborted.\n")
        outfile.write("ERROR: Cannot open the last changed date file. File move aborted.\n")

    #Go on to benchmark test
    log.stp("Part 2: Compare this invocation's result to the approved comparison benchmark.\n")
    outfile.write("Part 2: Compare this invocation's result to the approved comparison benchmark.\n")

    def logmsg(msg):
      log.stp(msg + "\n")
      outfile.write(msg + "\n")
    def logerr(msg):
      log.err(msg + "\n")
      outfile.write(msg + "\n")

    self.masterDict.pushLayer()
    compFlags = " "       ################
    seededBenchmark = False
    if "comparisonBenchmark" not in self.masterDict:
      # no comparison benchmark, try and find one from the seed site if it exists
      pathSeedInfo = self.masterDict.get("benchmarkSeedInfo", None)
      if not pathSeedInfo:
        logerr("No comparisonBenchmark specified and benchmarkSeedInfo not set, so no comparisons being done.")
        return False
      locSeedInfo = pullfile(pathSeedInfo,log) # bring seed info file local if its remote
      if not locSeedInfo:
        logerr("Unable to retrieve remote seed Info file.")
        return False
      xmlSeed = parseXml(locSeedInfo) # parse it
      testPath = self.masterDict["testPath"]
      seedPath = os.path.join(self.masterDict["benchmarkSeedSite"], testPath)
      seedNode = xmlSeed.findChild(seedPath) # find the current path, but prepended with the seed site
      if seedNode is None:
        logmsg("Node '%s' not found in seed info file." % seedPath)
        return False
      seedDict = parser.parseLines(seedNode.text)

      ##==Get comparison benchmark from remote host===

      if "comparisonBenchmark" not in seedDict:
        logerr("No benchmark declared in seed info file for comparisons. No comparisons being done.")
        return False
      else:
        logmsg("Comparison benchmark being ported from mainArchive and/or seed platform.")

      self.masterDict.pushLayer()
      self.masterDict.update({'siteDir':'<benchmarkSeedSite>'})
      comparisonBenchmark = self.masterDict.dereferencePointers(seedDict["comparisonBenchmark"])
      self.masterDict.popLayer()

      pathToBenchmark = os.path.join(self.masterDict["benchmarkSeedArchive"], comparisonBenchmark)

      if "errTol" not in self.masterDict:
        self.masterDict["errTol"] = str(self.masterDict.get("benchmarkSeedErrTol", "1.e-12"))
      if "partErrTol" not in self.masterDict:
        self.masterDict["partErrTol"] = str(self.masterDict.get("benchmarkSeedPartErrTol", "1.e-12"))
      seededBenchmark = True
    else:
      comparisonBenchmark = self.masterDict["comparisonBenchmark"]
      pathToBenchmark = os.path.join(pathToLocalArchive, comparisonBenchmark)
      if "sfocuFlags" in self.masterDict:
        compFlags = self.masterDict["sfocuFlags"]

    targetFilename = self.masterDict["checkpointBasename"] + self.masterDict["comparisonNumber"]
    pathToRunDir = self.masterDict["pathToRunDir"]
    pathToRunFile = os.path.join(pathToRunDir, targetFilename)

    retval2 = self.compareFiles(pathToRunFile, pathToBenchmark, compFlags)
    self.masterDict.popLayer()

    #if seededBenchmark:
    #  pushfile(remotePathToBenchmark) #this will delete locally pulled file
    if seededBenchmark and retval2:
      logmsg("Comparison of seeded benchmark was within tolerance, approving benchmark...")
      self.masterDict["testXmlNode"].text.append("comparisonBenchmark: <siteDir>/%s/<buildDir>/<runDir>/<checkpointBasename><comparisonNumber>" % self.masterDict["dateStr"])
      self.masterDict["testXmlNode"].smudge()

    #Test the restart against a restart benchmark.
    logmsg("Part 3: Compare this invocation's result to the approved restart benchmark.")
    retval3 = False

    targetFilename = self.masterDict["checkpointBasename"] + self.masterDict["restartNumber"]
    pathToRestartFile = os.path.join(pathToRunDir, targetFilename)

    if "restartBenchmark" not in self.masterDict:
      # transparency should have been tested and produced chk_restart_longrun_9f402yfg
      if retval2: # did comparison benchmark match?
        logmsg("Restart benchmark not present, testing for a transparent restart...")
        pathToLongChk = os.path.join(pathToRunDir, "chk_restart_longrun_9f402yfg")
        retval3 = self.compareFiles(pathToLongChk, pathToRestartFile, "")
        if retval3:
          logmsg("Restart transparency confirmed, approving restart benchmark in test xml file.")
          self.masterDict["testXmlNode"].text.append("restartBenchmark: <siteDir>/%s/<buildDir>/<runDir>/<checkpointBasename><restartNumber>" % self.masterDict["dateStr"])
          self.masterDict["testXmlNode"].smudge()
        else:
          logmsg("Restart was not transparent, not approving restart benchmark.")
      else:
        logerr("No restart benchmark specified and previous comparison failed, taking no action.")
    elif "restartNumber" not in self.masterDict:
      logerr("restartBenchmark not found in test.info for this test!")
    else:
      restartBenchmark = self.masterDict["restartBenchmark"]
      pathToRestartBenchmark = os.path.join(pathToLocalArchive, restartBenchmark)

      #make sure that the restart checkpoint exists locally
      if not os.path.isfile(pathToRestartFile):
        logerr("The restart test checkpoint file from this run was not found! %s" % pathToRestartFile)
      else:
        compFlags = " "
        if "sfocuFlags" in self.masterDict:
          compFlags = self.masterDict["sfocuFlags"]

        retval3 = self.compareFiles(pathToRestartFile, pathToRestartBenchmark, compFlags)

    return retval2 and retval3

#new tester for Chris's experimental IO tool.
#DEV: Stopgap until we get things properly intergrated into SFOCU

class CompositeTesterExperimentalIO(CompositeTester):

    #This is all we should need to override. -PR
  def compareFiles(self, pathToFile1, pathToFile2, compOptions):
    #return true if test is successful.  Return false if we encounter an error.

    #Let's break this out for readability sake.
    log = self.masterDict["log"] #from flashTest.py
    outfile = self.masterDict["outfile"] #from flashTest.py
    pathToFlash = self.masterDict["pathToFlash"] #from flashTest.py

    pathToCmpExpIO = self.masterDict.get("pathToCmpExpIO", os.path.join(pathToFlash, "tools", "cmpExpIO", "cmpExpIO"))
    cmpExpIOScript = self.masterDict.get("cmpExpIOScript", "cmpExpIO")

    cmdAndArgs = [cmpExpIOScript]
    cmdAndArgs.append(compOptions)
    # This tool takes no flags at the mo

    cmd = "%s %s %s" % (" ".join(cmdAndArgs), pathToFile1, pathToFile2)
    retval = self.compare(pathToFile1, pathToFile2, cmd)

    if not retval:
      return False #something catastrophically failed with sfocu.

    out, err, duration, exitStatus = retval

    if exitStatus == 0:
      log.stp("Process exit-status reports CmpExpIO ran successfully.")
      outfile.write("<b>CmpExpIO output:</b>\n" + out.strip() + "\n\n")

      if out.strip().endswith("SUCCESS"):
        log.stp("comparison of benchmark files yielded: SUCCESS")
        return True
      else:
        log.stp("comparison of benchmark files yielded: FAILURE")
        return False
    else:
      log.stp("Process exit-status reports CmpExpIO encountered an error")
      #record what we got before the error.
      outfile.write("Process exit-status retports CmpExpIO encountered an error\n" +
                    "<b>CmpExpIO output:</b>\n" + out.strip() + "\n\n")
      return False
    return True
