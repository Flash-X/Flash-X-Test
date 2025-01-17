#!/usr/bin/env python3
import sys, os, subprocess, pwd
import re, socket
from time import asctime, strftime, localtime
from shutil import copy
import locale

def main():

    # some variables used below and what they represent:
    #
    #             version: the version number for this "FlashTest"
    #     pathToFlashTest: absolute path up to and including the directory
    #                      directly containing the flashTest.py script
    #        pathToOutdir: absolute path up to and including the directory
    #                      to which all FlashTest output will be directed
    #       pathToSiteDir: absolute path up to and including the directory
    #                      which contains all output for a given platform.
    #             siteDir: the name of the above directory; the basename of
    #                      'pathToSiteDir' and the fully qualified domain
    #                      name of the host computer
    # pathToInvocationDir: absolute path up to and including the directory
    #                      which contains all FlashTest output for a given
    #                      invocation.
    #       invocationDir: the name of the above directory; the basename of
    #                      'pathToInvocationDir'
    #          pathToInfo: absolute path up to and including the file
    #                      containing all "test.info" data for this platform
    #                 log: the Logfile instance for this invocation of
    #                      "FlashTest"
    #       pathToPidFile: absolute path to a file that stores the process id for this "FlashTest"

    version = "1.0"
    owner = pwd.getpwuid(os.getuid())[0]
    pathToFlashTest = os.path.dirname(os.path.abspath(sys.argv[0]))

    pathToTmpDir = os.getenv("TMPDIR", "/tmp")
    if pathToTmpDir == "":
        pathToTmpDir = "/tmp"
    pathToPidFile = os.path.join(pathToTmpDir, "flashTest.pid")

    def __abort0(msg):
        """
    called for errors very early in the initial invocation of FlashTest

    Because no logfile is instantiated yet, we try to record 'msg'
    in a file "ERROR" in the top-level FlashTest directory.

    This function does not attempt to remove a pidFile if it exists.
    """
        print(msg)
        # ignore failure of writing to the ERROR file in pathToFlashTest
        try:
            open(os.path.join(pathToFlashTest, "ERROR"), "a").write(
                "%s: %s\n" % (asctime(), msg)
            )
        except OSError:
            pass
        sys.exit(1)

    def __abort(msg):
        """
    called for errors in the initial invocation of FlashTest

    Because logfile may not be instantiated yet, we try to record 'msg'
    in a file "ERROR" in the top-level FlashTest directory.

    This function attempts to remove an existing pidFile on the way out.
    """
        print(msg)
        # ignore failure of writing to the ERROR file in pathToFlashTest
        try:
            open(os.path.join(pathToFlashTest, "ERROR"), "a").write(
                "%s: %s\n" % (asctime(), msg)
            )
        except OSError:
            pass
        finally:
            pidFile.unregisterPid(pathToPidFile)  # remove /tmp/flashTest.pid file before aborting
        sys.exit(1)

    def __deleteFiles(startDir):
        """
    Recursively search each directory under 'startDir' for text
    files named "files_to_delete", which will have been written
    by the test objects during run time, and which name files in
    that directory which should be deleted after the invocation
    has been archived.

    If a "files_to_delete" file is present, another file called
    "deleted_files" will be created, listing all files that were
    successfully deleted as well as any that were not found.

    The original "files_to_delete" file will itself be deleted
    in all cases.
    """

        def __delete():
            items = os.listdir(".")
            cwd = os.getcwd()
            deletedFiles = []
            notFound = []
            for item in items:
                if os.path.isdir(item):
                    os.chdir(item)
                    __delete()
                    os.chdir(cwd)
                elif item == "files_to_delete":
                    filesToDelete = parser.fileToList(item)
                    print("files to delete")
                    os.remove("files_to_delete")

                    for fileToDelete in filesToDelete:
                        if os.path.isfile(fileToDelete):
                            os.remove(fileToDelete)
                            deletedFiles.append(fileToDelete)
                        else:
                            notFound.append(
                                fileToDelete + " (not found or not a file) "
                            )

                    deletedFiles.extend(notFound)
                    if deletedFiles:
                        open("deleted_files", "w").write("\n".join(deletedFiles))

        cwd = os.getcwd()
        os.chdir(startDir)
        __delete()
        os.chdir(cwd)

    def __incErrors(whichStage):
        """
    Take a path and a stage 0-3, which corresponds to the stage
    of testing where the error occurred (0=setup, 1=compilation,
    2=execution, 3=testing) and note the error in "errors" files
    at all appropriate levels.
    """
        # masterDict["changedFromPrevious"] should be set by the test
        # object's tester component if we reached the testing stage and
        # found that the results of the test differed from those of the
        # previous invocation.
        # masterDict["sameAsPrevious"] should be set by the test
        # object's tester component if we reached the testing stage and
        # found that the results of the test differed from those of the
        # previous invocation.
        changedFromPrevious = masterDict.has_key("changedFromPrevious")
        if (whichStage == 3) and not changedFromPrevious:
            sameAsPrevious = masterDict.has_key("sameAsPrevious")
        else:
            sameAsPrevious = False

        # Note the error at the RUN LEVEL (if we've gotten that far)
        if masterDict.activeLayer >= 3:  # A run dir has been generated
            # with an "errors" file inside.
            # This "errors" file has only 2 or 3 lines:
            #
            # 0/1: no error/error during execution stage
            # 0/1: no error/error during testing stage
            # !/=: result of test differs from that of previous invocation/
            #                     is same as previous invocation
            #      3rd line may be absent, in which case comparison against
            #      previous result failed for reasons other than differences
            #      in the checkpoints; most likely because the "previous"
            #      checkpoint could not be found.
            errorsFile = os.path.join(pathToRunDir, "errors")
            if whichStage == 2:
                errorLines = ["1", "0"]
            elif whichStage == 3:
                errorLines = ["0", "1"]
                if changedFromPrevious:
                    errorLines.append("!")
                elif sameAsPrevious:
                    errorLines.append("=")

            open(errorsFile, "w").write("\n".join(errorLines))

        # Note the error at the BUILD LEVEL (if we've gotten that far)
        if masterDict.activeLayer >= 1:  # A build directory
            # hopefully has been generated
            # with an "errors" file inside.
            # This "errors" file has 6 or 7 lines:
            #
            # 0/1: no error/error during setup stage
            # 0/1: no error/error during compilation stage
            # 0/n: no errors/n errors during execution stage
            # 0/n: no errors/n errors during testing stage
            #  n : total number of runs attempted ( = num parfiles)
            # 0/n: no errors/n errors during testing that are same as before
            #      (included in numbers on 4th line)
            #  ! : results of 1 or more tests in this build differed
            #      from those of the previous invocation.
            errorsFile = os.path.join(pathToBuildDir, "errors")
            errorLines = parser.fileToList(errorsFile)

            if len(errorLines) == 6:
                if changedFromPrevious:
                    errorLines.append("!")
            else:  # can assume len(errorLines) is 7 with a "!" at the end
                # if this build has had *any* run whose results differed from
                # those of the previous invocation, set 'changedFromPrevious'
                # to True regardless of whether *this* run's results differed
                # or not. This will make sure the "!" gets put on the end of
                # the appropriate line at the invocation level (see below)
                changedFromPrevious = True

            # increment the value in stage 'whichStage' by 1
            errorLines[whichStage] = str(int(errorLines[whichStage]) + 1)
            if (whichStage == 3) and sameAsPrevious:
                errorLines[5] = str(int(errorLines[5]) + 1)
            open(errorsFile, "w").write("\n".join(errorLines))

            # we actually need these a few lines down
            # for the increment at the invocation level
            numExecErrs = int(errorLines[2])
            numTestErrs = int(errorLines[3])
            totalRuns = int(errorLines[4])
            numTestSameErrs = int(errorLines[5])
        #     else:   # if masterDict.activeLayer < 1
        #       numExecErrs = int(errorLines[2])
        #       numTestErrs = int(errorLines[3])
        #       totalRuns   = int(errorLines[4])
        #       numTestSameErrs = int(errorLines[5])

        # note the error at the INVOCATION LEVEL
        # This "errors" file contains names of all builds which yielded
        # some kind of error, noting the number of failed runs or tests
        # if the test failed in the execution or testing stages.
        errorsFile = os.path.join(pathToInvocationDir, "errors")
        errorLines = parser.fileToList(errorsFile)

        # compose err message
        if whichStage == 0:
            errMsg = "failed in setup"
        elif whichStage == 1:
            errMsg = "failed in compilation"
        elif whichStage == 2:
            errMsg = "%s/%s failed in execution" % (numExecErrs, totalRuns)
            if numTestErrs > 0:
                errMsg = "%s; %s/%s failed in testing" % (
                    errMsg,
                    numTestErrs,
                    totalRuns,
                )
                if numTestSameErrs > 0:
                    if numTestSameErrs == numTestErrs:
                        errMsg = errMsg + " as before"
                    else:
                        errMsg = "%s, % as before" % (errMsg, numTestSameErrs)
        elif whichStage == 3:
            errMsg = "%s/%s failed in testing" % (numTestErrs, totalRuns)
            if numTestSameErrs > 0:
                if numTestSameErrs == numTestErrs:
                    errMsg = errMsg + " as before"
                else:
                    errMsg = "%s, %s as before" % (errMsg, numTestSameErrs)
            if numExecErrs > 0:
                errMsg = "%s/%s failed in execution; %s" % (
                    numExecErrs,
                    totalRuns,
                    errMsg,
                )
        errMsg = "%s - %s" % (buildDir, errMsg)
        if changedFromPrevious:
            # add a "!" if changed from previous invocation's results
            errMsg = errMsg + " - !"

        for i in range(len(errorLines)):
            # if the invocation-level errors file already has
            # data about this build, replace it with 'errMsg'
            if errorLines[i].split(" - ", 1)[0] == buildDir:
                errorLines[i] = errMsg
                break
        else:
            # otherwise append it
            errorLines.append(errMsg)
            errorLines.sort()

        open(errorsFile, "w").write("\n".join(errorLines))

    ##########################
    ##  PARSE COMMAND LINE  ##
    ##########################

    # options to FlashTest which take no arguments
    # DEV should be able to adjust this in Config
    # especially now that "-u" is a custom option
    standAloneOpts = ["-t", "-u", "-v", "-vv", "-L", "--force"]

    # Retrieve a two-tuple for this invocation where the first element is
    # a dictionary of options (with arguments, if applicable) to FlashTest,
    # and the second element is a list of two-tuples, each containing a
    # test-path and a dictionary of options specific to that test.
    #
    # Graphically, the structure of the return value of 'parseCommandLine'
    # looks like:
    # ( { FlashTest-opt1: FlashTest-val1,
    #     FlashTest-opt2: FlashTest-val2 },
    #   [ ( test-path1, { test-path1-opt1: test-path1-val1,
    #                     test-path1-opt2: test-path1-val2 } ),
    #     ( test-path2, { test-path2-opt1: test-path2-val1 } ) ] )
    flashTestOpts, pathsAndOpts = parser.parseCommandLine(sys.argv[1:], standAloneOpts)

    # -------------------------------------------------------#
    # Check no other flashTest process is currently running
    # and/or prevent other instances from running
    # -------------------------------------------------------#
    if not pidFile.registerPid(pathToPidFile, "--force" in flashTestOpts):
        __abort0("It seems a flashTest process is already running. \n Use --force or delete %s to run this flashTest anyway." % (pathToPidFile,))

    # see if user has specified a separate "config"
    if "-c" in flashTestOpts:
        pathToConfig = flashTestOpts["-c"]
    else:
        pathToConfig = os.path.join(pathToFlashTest, "config")

    if "-e" in flashTestOpts:
        pathToExeScript = flashTestOpts["-e"]
    else:
        pathToExeScript = os.path.join(pathToFlashTest, "exeScript")

    #########################
    ##  PARSE CONFIG FILE  ##
    #########################

    if os.path.isfile(pathToConfig):
        try:
            configDict = parser.parseFile(pathToConfig)
        except Exception as e:
            __abort('Error opening "config" file\n' + str(e))
    else:
        __abort(
            'Configuration file "%s" does not exist or is not a file.' % pathToConfig
        )
    #########################
    ##  MASTER DICTIONARY  ##
    #########################

    # The master dictionary which we'll pass to the test object begins
    # life as a LayeredDict with initial keys and values copied from
    # 'configDict' (the copy is implicit in the initialization)
    masterDict = LayeredDict(configDict)

    masterDict["version"] = version
    masterDict["owner"] = owner
    masterDict["pathToFlashTest"] = pathToFlashTest
    masterDict["flashTestOpts"] = flashTestOpts
    masterDict["pathToExeScript"] = pathToExeScript

    ###########################
    ##  CHECK FOR -f OPTION  ##
    ###########################

    if "-f" in flashTestOpts:
        pathToJobFile = flashTestOpts["-f"]
        if not pathToJobFile:
            __abort(
                "The '-f' option must be followed by a path to a text file\n"
                + "consisting of a newline-delimited list of tests"
            )
        # else
        if not os.path.isfile(pathToJobFile):
            __abort('"%s" does not exist or is not a file.' % pathToJobFile)

        # Extend 'pathsAndOpts' to include test-paths read in from a file.
        # See comments to "parseCommandLine()" above for more details
        lines = parser.fileToList(pathToJobFile)

        # briefly re-join the 'lines' list into a single string,
        # with a single space inserted between list elements, then
        # re-split the new string by breaking on all whitespace.
        if lines:
            lines = re.split("\s*", " ".join(lines))

        pathsAndOpts.extend(parser.getPathsAndOpts(lines))

    if len(pathsAndOpts) == 0:
        __abort(
            "There are no tests to run. You must provide the name of at\n"
            + 'least one test or path to at least one "test.info" file.'
        )

    # else
    masterDict["pathsAndOpts"] = pathsAndOpts

    # get "test.info" data, if necessary
    masterInfoNode = None

    # Do a preliminary run through all our tests to see if any will require
    # data from a "test.info" file. If so, parse that data into an instance
    # of class XmlNode for use in all tests that require it, copying the
    # "test.info" file to the local machine from a remote host if necessary.
    if "-i" in flashTestOpts:
        # get 'pathToInfo' value from command-lines
        pathToInfo = flashTestOpts["-i"]
        if not os.path.isfile(pathToInfo):
            __abort('"%s" does not exist or is not a file.' % pathToInfo)
    else:
        # get 'pathToInfo' value from "config" or, if it's not there,
        # from the default location under 'pathToFlashTest'
        pathToInfo = masterDict.get(
            "pathToInfo", os.path.join(pathToFlashTest, "test.info")
        )

    # split 'pathToInfo' into its hostname and path segments
    if pathToInfo.count(":") > 0:
        infoHost, pathToInfo = pathToInfo.split(":", 1)
        if infoHost == "localhost":
            infoHost = ""
    else:
        infoHost = ""

    masterDict["infohost"] = infoHost
    masterDict["pathToInfo"] = pathToInfo

    # initializing variable
    masterDict["environment"] = ""

    for testPath, overrideOptions in pathsAndOpts:
        if testPath.count(os.sep) > 0:
            # At least one test in this invocation requires "test.info" data
            # so obtain the text of the "test.info" file whether it resides
            # on a remote computer or locally.
            if infoHost:
                # "test.info" file is on a remote computer
                pathToTmp = os.path.join(pathToFlashTest, "tmp")

                cmd = "scp %s:%s %s" % (infoHost, pathToInfo, pathToTmp)
                out, err, duration, exitStatus = getProcessResults(cmd)
                if err:
                    __abort(
                        'Unable to retrieve "%s:%s"\n%s' % (infoHost, pathToInfo, err)
                    )
                # else
                if exitStatus != 0:
                    __abort(
                        'Exit status %s indicates error retrieving "%s:%s"'
                        % (exitStatus, infoHost, pathToInfo)
                    )
                # else the file should have been transfered
                filename = os.path.basename(pathToInfo)
                if not os.path.isfile(os.path.join(pathToTmp, filename)):
                    __abort('File "%s" not found in "%s"' % (filename, pathToTmp))
                # else
                try:
                    masterInfoNode = parseXml(os.path.join(pathToTmp, filename))
                except Exception as e:
                    __abort('Error parsing "%s:%s"\n%s' % (infoHost, pathToInfo, e))

                # remove the copied file from "tmp"
                os.remove(os.path.join(pathToTmp, filename))

            else:
                # "test.info" file is local
                if not os.path.isfile(pathToInfo):
                    __abort('"%s" does not exist or is not a file' % pathToInfo)

                # else
                try:
                    masterInfoNode = parseXml(pathToInfo)
                except Exception as e:
                    __abort('Error parsing "%s"\n%s' % (pathToInfo, e))

            # 'masterInfoNode' now encapsulates all "test.info" data.
            # Break out of the for-loop.
            break

    #############################
    ##  GENERATE pathToOutdir  ##
    #############################

    pathToOutdir = flashTestOpts.get("-o", "")
    if not pathToOutdir:
        # check if we got a path to the outdir from the config file,
        # else use directory named "output" inside FlashTest directory
        pathToOutdir = masterDict.get(
            "pathToOutdir", os.path.join(pathToFlashTest, "output")
        )

    # create it if it doesn't exist
    if not os.path.exists(pathToOutdir):
        try:
            os.mkdir(pathToOutdir)
        except:
            __abort("Unable to create directory %s" % pathToOutdir)

    # make sure we have an absolute path
    pathToOutdir = os.path.abspath(pathToOutdir)

    masterDict["pathToOutdir"] = pathToOutdir

    ########################
    ##  GENERATE siteDir  ##
    ########################

    # try to determine the fully qualified domain name of the host
    if masterDict.has_key("FQHostname"):
        FQHostname = masterDict["FQHostname"]
    else:
        # DEV must allow a mechanism for dealing with aliases
        # DEV need a better mechanism for figuring out computer name
        # DEV when on a wireless network
        # DEV Also, if gethostbyaddr doesn't work, flashTest.py will
        # crash even tho it's not necessary - FQHostname only needs
        # to be defined if 'site' is not (see below)
        try:
            FQHostname = socket.gethostbyaddr(socket.gethostname())[0]
        except:
            FQHostname = "<HOSTNAME>"

        masterDict["FQHostname"] = FQHostname
    # Determine value of "site". This will be the first element of
    # 'FQHostname' unless the user has specified it with the "-s"
    # command-line option or by declaring "site" in "config"
    if "-s" in flashTestOpts:
        # get the site from the command line
        siteDir = flashTestOpts["-s"]
    elif "site" in masterDict:
        # get the site from the config file
        siteDir = masterDict["site"]
    else:
        # 'siteDir' will be the first element of the fully-qualified
        # hostname as returned by socket.gethostname(). i.e. if the
        # fully-qualified hostname has a "." in it, 'siteDir' will
        # be everything that comes before that "."
        siteDir = FQHostname.split(".", 1)[0]

    pathToSiteDir = os.path.join(pathToOutdir, siteDir)

    # create it if it doesn't exist
    if not os.path.exists(pathToSiteDir):
        try:
            os.mkdir(pathToSiteDir)
        except:
            __abort("Unable to create directory %s" % pathToSiteDir)

    masterDict["pathToSiteDir"] = pathToSiteDir
    masterDict["siteDir"] = siteDir

    # TODO: Find an elegant way to do this
    # This is a hacky way to change 'flashSite' dir
    # through command line options and make it conistent
    # with 'siteDir'. 
    masterDict["flashSite"] = str(siteDir)

    ##############################
    ##  GENERATE invocationDir  ##
    ##############################

    # Generate a directory to hold all output from this invocation of FlashTest
    # Its name will be the current day's date, plus a suffix if necessary

    # start by getting the date in YYYY-MM-DD format
    dateStr = strftime("%Y-%m-%d", localtime())

    # get a list of any dirs in "output" that already start with dateStr
    dirs = [
        item
        for item in os.listdir(pathToSiteDir)
        if (
            os.path.isdir(os.path.join(pathToSiteDir, item))
            and item.startswith(dateStr)
        )
    ]

    if len(dirs) > 0:
        suffixes = [dir[len(dateStr) :].strip("_") for dir in dirs]
        suffixes.sort()
        highestSuffix = suffixes[len(suffixes) - 1]
        if highestSuffix == "":
            newSuffix = 2
        else:
            newSuffix = int(highestSuffix) + 1
        # there has already been at least one invocation
        # of FlashTest on this date, so add a suffix
        dateStr = "%s_%s" % (dateStr, newSuffix)
    masterDict["dateStr"] = dateStr
    invocationDir = dateStr
    pathToInvocationDir = os.path.join(pathToSiteDir, invocationDir)

    # create invocationDir
    try:
        os.mkdir(pathToInvocationDir)
    except:
        __abort("Unable to create directory %s" % pathToInvocationDir)

    # create a ".lock" file so that FlashTestView
    # will ignore it until the invocation is complete
    open(os.path.join(pathToInvocationDir, ".lock"), "w").write("")

    # Create a file "errors" which will record the details
    # of all errors that happen during this invocation.
    #
    # This file will be the basis of the floating statistics
    # box that appears in FlashTestView when the user hovers
    # over an invocation link (i.e. a date).
    #
    # See the comments to "__incErrors()" for more details
    open(os.path.join(pathToInvocationDir, "errors"), "w").write("")

    # Write a copy of the level-0 dictionary of 'masterDict'
    # (which at this point contains everything in 'masterDict')
    # into the invocation directory as a newline-delimited list
    # of key-value pairs
    keysAndVals = [
        "%s: %s" % (key, masterDict.dicts[0][key]) for key in masterDict.dicts[0]
    ]
    open(os.path.join(pathToInvocationDir, "masterDict"), "w").write(
        "\n".join(keysAndVals)
    )

    masterDict["pathToInvocationDir"] = pathToInvocationDir
    masterDict["invocationDir"] = invocationDir

    ###########################
    ##  INSTANTIATE LOGFILE  ##
    ###########################

    log = Logfile(pathToInvocationDir, "flash_test.log", "-v" in flashTestOpts)
    log.info("FlashTest v%s started by %s on %s\n" % (version, owner, asctime()), False)
    log.info(
        "Original command-line: %s %s" % (sys.argv[0], " ".join(sys.argv[1:])), False
    )
    log.info("This invocation: %s" % invocationDir, False)
    # find python version
    log.info("Python version info:", False)
    log.info(sys.version, True)
    try:
        cwd = os.getcwd()
    except Exception as e:
        __abort("Initial getcwd: " + str(e))
    try:  # find svn version
        os.chdir(pathToFlashTest)
        log.info("FlashTest version info:", False)
        p = subprocess.Popen(
            ["svn", "info", os.getcwd()], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        log.info(p.communicate()[0], True)
    except:
        pass
    os.chdir(cwd)
    log.brk()

    masterDict["log"] = log

    #######################################################
    ##  CHECK FOR PREVIOUS INVOCATION'S ARCHIVE RESULTS  ##
    #######################################################

    if "-t" not in flashTestOpts:
        previousArchiveLog = os.path.join(pathToSiteDir, "archive.log")
        if os.path.isfile(previousArchiveLog):
            archiveText = open(previousArchiveLog, "r").read()
            log.info(archiveText, False)
            log.brk()

    ######################
    ##  ARCHIVE OBJECT  ##
    ######################
    # provides methods for communication with the remote archive
    pathToLocalArchive = masterDict.get(
        "pathToLocalArchive", os.path.join(pathToFlashTest, "localArchive")
    )
    if not os.path.isabs(pathToLocalArchive):
        pathToLocalArchive = os.path.join(pathToFlashTest, pathToLocalArchive)
        log.note('Using "%s" as path to local archive.' % pathToLocalArchive)

    masterDict["pathToLocalArchive"] = pathToLocalArchive

    mainArchiveHost = ""
    pathToMainArchive = masterDict.get("pathToMainArchive", "")
    if pathToMainArchive:
        # work out if the main archive resides on a remote computer
        if pathToMainArchive.count(":") > 0:
            mainArchiveHost, pathToMainArchive = pathToMainArchive.split(":", 1)
            if mainArchiveHost == "localhost":
                mainArchiveHost = ""

    masterDict["mainArchiveHost"] = mainArchiveHost
    masterDict["pathToMainArchive"] = pathToMainArchive

    viewArchiveHost = ""
    pathToViewArchive = masterDict.get("pathToViewArchive", "")
    if pathToViewArchive:
        # work out if the view archive resides on a remote computer
        if pathToViewArchive.count(":") > 0:
            viewArchiveHost, pathToViewArchive = pathToViewArchive.split(":", 1)
            if viewArchiveHost == "localhost":
                viewArchiveHost = ""

    masterDict["viewArchiveHost"] = viewArchiveHost
    masterDict["pathToViewArchive"] = pathToViewArchive

    logArchiveHost = ""
    pathToLogArchive = masterDict.get("pathToLogArchive", "")
    if pathToLogArchive:
        # work out if the log archive resides on a remote computer
        if pathToLogArchive.count(":") > 0:
            logArchiveHost, pathToLogArchive = pathToLogArchive.split(":", 1)
            if logArchiveHost == "localhost":
                logArchiveHost = ""

    masterDict["logArchiveHost"] = logArchiveHost
    masterDict["pathToLogArchive"] = pathToLogArchive

    arch = Archive(log, masterDict)
    masterDict["arch"] = arch

    #######################
    ##  BEGIN FLASHTEST  ##
    #######################

    try:
        testObject = TestObject(masterDict)
    except Exception as e:
        __abort(str(e))

    try:
        buildDir = "ALL"
    except:
        pass

    # else testObject is now successfully instantiated
    if testObject.entryPoint1() == False:  # user's 1st chance to interrupt
        __incErrors(0)
    else:
        # outer loop over all test tuples, where each test tuple contains a
        # test name and a list of secondary "build tuples". Each build tuple,
        # in turn, consists of a short path to the relevant "test.info" file
        # (or the empty string if no info file was indicated), and the list of
        # override-options to the test, if any
        for testPath, overrideOptions in pathsAndOpts:
            # some variables used below and what they represent:
            # (see also comments at top of file)
            #
            #        testPath: xml-path to a node in "test.info" which contains
            #                  data relevant to a single FlashTest build
            #  pathToBuildDir: absolute path up to and including the directory
            #                  which contains all output for a single build, and
            #                  which contains one or more instances of 'runDir'
            #                  (see below).
            #        buildDir: The basename of 'pathToBuildDir', an immedidate
            #                  sub-directory of 'invocationDir'
            #    pathToRunDir: absolute path up to and including the directory
            #                  which directly contains all output for one run
            #                  of the executable against a single set of runtime
            #                  parameters.
            #          runDir: The basename of 'pathToRunDir', an immediate sub-
            #                  directory of 'buildDir'
            masterDict.setActiveLayer(1)
            masterDict["testPath"] = testPath
            masterDict["overrideOptions"] = overrideOptions

            # start log entry for this build
            log.brk()
            shortPathToNode = os.path.normpath(os.path.join(siteDir, testPath))

            if testPath.count(os.sep) > 0:
                thisNode = masterInfoNode.findChild(shortPathToNode)

                if not thisNode:
                    # 'testPath' led to a non-existant node,
                    if infoHost:
                        log.err(
                            '%s does not exist in "%s:%s"\n'
                            % (shortPathToNode, infoHost, pathToInfo)
                            + "Aborting this build."
                        )
                    else:
                        log.err(
                            '%s does not exist in "%s"\n'
                            % (shortPathToNode, pathToInfo)
                            + "Aborting this build."
                        )
                    continue

                # else
                infoData = "\n".join(
                    [line.strip() for line in thisNode.text if len(line.strip()) > 0]
                )

                if len(infoData) == 0:
                    if infoHost:
                        log.err(
                            '%s exists in "%s:%s", but contains no info data.\n'
                            % (shortPathToNode, infoHost, pathToInfo)
                            + "Aborting this build."
                        )
                    else:
                        log.err(
                            '%s exists in "%s", but contains no info data.\n'
                            % (shortPathToNode, pathToInfo)
                            + "Aborting this build."
                        )
                    continue

                infoOptions = parser.parseLines(thisNode.text)
                log.stp('Parsed "%s"' % shortPathToNode)
                masterDict["testXmlNode"] = thisNode
            else:
                log.info('No "test.info" data provided')
                infoOptions = {}

            # determine 'buildDir', which will hold output from this individual build
            buildDir = os.path.normpath(testPath).replace(os.sep, "_")

            # determine absolute path to buildDir
            pathToBuildDir = os.path.join(pathToInvocationDir, buildDir)
            log.stp('Creating directory "%s"' % pathToBuildDir)

            if os.path.isdir(pathToBuildDir):
                # a directory of this name already exists[0]
                log.err(
                    'A directory called "%s" already exists.\n' % pathToBuildDir
                    + "Skipping this build."
                )
                continue

            # else
            try:
                os.mkdir(pathToBuildDir)
            except Exception as e:
                log.err("%s\n" % str(e) + "Skipping this build.")
                continue

            masterDict["pathToBuildDir"] = pathToBuildDir
            masterDict["buildDir"] = buildDir

            # enter override-options and "test.info" options into 'masterDict'
            # "test.info" options will temporarily overwrite override-options,
            # for the sake of constructing a good message to the user
            masterDict.update(overrideOptions)
            masterDict.update(infoOptions)

            # override-options take precedence over options with the same
            # name from the "test.info" file. Note in logfile if this happens.
            for key in overrideOptions:
                if key in masterDict and masterDict[key] != overrideOptions[key]:
                    log.note(
                        'key "%s" with value "%s" overridden by new value "%s"'
                        % (key, masterDict[key], overrideOptions[key])
                    )
                    masterDict[key] = overrideOptions[key]

            if testPath.count(os.sep) > 0:
                # Record the text of the original "test.info" data in the logfile
                log.info('****** "test.info" ******')
                log.info(infoData)
                log.info("*************************")

                # Record a copy of 'infoData' in this build's output directory.
                # The first line is an xml node-path to the original "test.info"
                # data, which FlashTestView uses to generate a link to the info-
                # file manager.
                msg = shortPathToNode + "\n\n"
                msg += infoData + "\n"
                open(os.path.join(pathToBuildDir, "test.info"), "w").write(msg)

            #####################
            ##  "errors" File  ##
            #####################

            # Creates a file "errors" which will record the number of
            # errors encountered for one build/series of runs as well
            # as the total number of parfiles intended to be run. The
            # file is a text file with 6 lines: one line each for the
            # number of errors in setup and compilation (will be 0 or
            # 1), one line each for the number of errors occurring in
            # runtime and in testing, a line for the total
            # number of parfiles that were to be tried in this build,
            # and finally a line for the number of errors in testing
            # that were "as before" (those are also included in the
            # number on the 4th line).
            startVals = "0\n0\n0\n0\n0\n0"
            open(os.path.join(pathToBuildDir, "errors"), "w").write(startVals)

            # The user can interfere again here if he/she wants, e.g.
            # to control what object is put in place for 'testObject's'
            # "setupper" and "compiler" members or to add an instruction
            # instruction to FlashTestView regarding what kind of a menu
            # item to generate on the "view builds" screen.
            testObject.entryPoint2()

            # Now that information from the "test.info" file has been
            # read in, add instances of strategy classes for setup,
            # compilation, execution, and testing stages.
            for keyword in ["setupper", "compiler"]:
                testObject.installComponent(keyword)

            #############
            ##  SETUP  ##
            #############
            log.info("** setup phase **")
            if testObject.setup() == False:
                __incErrors(0)
                continue

            ###################
            ##  COMPILATION  ##
            ###################
            log.info("** compilation phase **")
            if testObject.compile() == False:
                __incErrors(1)
                continue

            #################
            ##  TRANSFERS  ##
            #################
            transfers = masterDict.get("transfers", [])
            if len(transfers) > 0:
                # change space-delimited 'transfers' into a python list
                transfers = parser.stringToList(transfers)

            # make copies in output directory of any files in 'transfers'
            transferedFiles = []
            for path in transfers:
                # 'path' is assumed to be a relative path to the file
                # from the top-level directory of the FLASH source
                # Split this into path and basename
                path, file = os.path.split(path)
                log.info('Transfering file "%s"' % file)
                # HACK - this 'pathToFlash' stuff will be gone in next iteration
                pathToFlash = masterDict["pathToFlash"]
                if os.path.isfile(os.path.join(pathToFlash, path, file)):
                    copy(os.path.join(pathToFlash, path, file), pathToBuildDir)
                    transferedFiles.append(file)
                elif os.path.isdir(os.path.join(pathToFlash, path, file)):
                    os.symlink(
                        os.path.join(pathToFlash, path, file),
                        os.path.join(pathToBuildDir, file),
                    )
                    transferedFiles.append(file)
                else:
                    log.warn('File "%s" was not found in "%s"' % (file, path))

            # +-------------------+
            # |  EXTRA TRANSFERS  |
            # +-------------------+
            if masterDict.has_key("extraTransfers"):
                transfers = masterDict["extraTransfers"]
                if len(transfers) > 0:
                    # change space-delimited 'transfers' into a python list
                    transfers = parser.stringToList(transfers)

                    # make copies in output directory of any files in 'transfers' and append
                    # names to transferedFiles - if they exist.
                    for path in transfers:
                        # As above: 'path' is assumed to be a relative path to the file
                        # from the top-level directory of the FLASH source
                        # Split this into path and basename
                        path, file = os.path.split(path)
                        # HACK - this 'pathToFlash' stuff will be gone in next iteration
                        pathToFlash = masterDict["pathToFlash"]
                        if os.path.isfile(os.path.join(pathToFlash, path, file)):
                            #              log.info("os.path.join(pathToFlash=\"%s\",path=\"%s\",file=\"%s\") is \"%s\", pathToBuildDir is \"%s\".\n" %
                            #                       (pathToFlash, path, file, os.path.join(pathToFlash, path, file), pathToBuildDir))
                            copy(os.path.join(pathToFlash, path, file), pathToBuildDir)
                            transferedFiles.append(file)
                            log.info('Transferring extra file "%s"' % file)

            ##      log.info("transferedFiles is %s.\n" % transferedFiles)

            ################
            ##  PARFILES  ##
            ################
            parfiles = parser.stringToList(masterDict.get("parfiles", ""))
            masterDict["parfiles"] = parfiles

            if len(parfiles) > 0:
                # set number of parfiles to be run on fifth line of "errors" file
                errorsFile = os.path.join(pathToBuildDir, "errors")
                lines = open(errorsFile, "r").readlines()
                lines[4] = str(len(parfiles)) + "\n"
                open(errorsFile, "w").write("".join(lines))

            # DEV another entry point here for changing transfers and parfiles?

            #################
            ##  EXECUTION  ##
            #################
            if len(parfiles) > 0:
                log.info("** execution phase **")
            else:
                log.warn(
                    "Since parfiles is empty, there will be no execution or testing phases."
                )

            # inner loop over each parfile listed for a single executable
            for parfile in parfiles:

                if os.path.isabs(parfile):
                    if os.path.isfile(parfile):
                        parfileText = open(parfile).read()
                        parfile = os.path.basename(parfile)
                    else:
                        __incErrors(2)
                        log.err(
                            'Parfile "%s" not found\n' % parfile + "Skipping this run."
                        )
                        continue

                else:
                    __incErrors(2)
                    log.err(
                        'Parfiles specified in a "test.info" file such as "%s"\n'
                        % parfile
                        + "must be declared as absolute paths. Skipping this run."
                    )
                    continue

                # define the name of the directory that will hold all results from this run
                firstDot = parfile.find(".")
                if firstDot > 0:
                    runDir = parfile[:firstDot]  # truncate any dot and following chars
                    # (essentially to truncate the '.par')
                pathToRunDir = os.path.join(pathToBuildDir, runDir)

                if os.path.isdir(pathToRunDir):
                    # a directory of this name already exists in 'buildDir'
                    __incErrors(2)
                    log.err(
                        "There is already a directory called '%s' in %s\n"
                        % (runDir, pathToBuildDir)
                        + "Skipping this run."
                    )
                    continue
                # else all is well - The last level of nested directories will be
                # for the output of the run against this parfile
                os.mkdir(pathToRunDir)

                # set 'masterDict' layer to 2 and erase any keys previously set
                # at this layer, i.e. in an earlier iteration of the loop
                masterDict.setActiveLayer(2)

                masterDict["runDir"] = runDir
                masterDict["pathToRunDir"] = pathToRunDir

                # make links in 'runDir' to any transfers we had
                for transferedFile in transferedFiles:
                    try:
                        os.link(
                            os.path.join(pathToBuildDir, transferedFile),
                            os.path.join(pathToRunDir, transferedFile),
                        )
                    except OSError as e:
                        log.warn('Linking "%s" failed: %s' % (transferedFile, str(e)))

                # write the parfile into our new directory
                open(os.path.join(pathToRunDir, parfile), "w").write(parfileText)

                masterDict["pathToParfile"] = os.path.join(pathToRunDir, parfile)
                masterDict["parfile"] = parfile

                # create an "errors" file at the run level whose value will be
                # "00" (no errors), "10" (error during runtime) or "01" (error
                # during the testing phase)
                open(os.path.join(pathToRunDir, "errors"), "w").write("0\n0")

                # The user can interfere again here if he/she wants, e.g.
                # to control what object is put in place for 'testObject's'
                # "executer" and "tester" members
                testObject.entryPoint3()

                for keyword in ["executer", "tester"]:
                    testObject.installComponent(keyword)

                # run the executable
                if testObject.execute() == False:
                    __incErrors(2)
                    continue

                ############
                ##  TEST  ##
                ############
                log.info("** testing phase **")
                if testObject.test() == False:
                    __incErrors(3)

                # +-------------------------------------+
                # COPY COMPLETED TEST TO VIEW ARCHIVE  +
                # +-------------------------------------+

                # Check -t
    if "-vv" in flashTestOpts and "-t" not in flashTestOpts:
        # send to view archive

        if pathToViewArchive:
            log.stp("Sending copy of completed test output to view archive...")

            try:
                arch.sendToViewArchive(incremental=True)
            except Exception as e:
                log.err("%s\n" % e + "No copy of output sent to view archive.")
            else:
                log.stp("Incremental copy of output sent to view archive.")

    #############################
    ##  ARCHIVING AND CLEANUP  ##
    #############################

    log.stp("All tests completed.")
    # pathToInfo is real name, make this work remotely
    if masterInfoNode.dirty:
        log.stp("Info node has been modified, updating file.")
        try:

            def delta(old):
                remote = parseXmlString(old)
                remote.mergeDirtyFrom(masterInfoNode)
                return "".join(x + "\n" for x in remote.getXml())

            remoteFile.updatefile("%s:%s" % (infoHost, pathToInfo), delta)
        except Exception as e:
            log.err("Failed to update info node: " + str(e))

    if "-L" in flashTestOpts:
        if pathToLogArchive:
            log.stp("Sending log files to log archive...")
            try:
                arch.sendToLogArchive(False)
            except Exception as e:
                log.err("%s\n" % e + "No log files sent to log archive.")
            else:
                log.stp("Log files sent to log archive.")

    with open(os.path.join(pathToSiteDir,"invocation.toml"), "w") as invocationToml:
        invocationToml.write(f'INVOCATION_DIR="{invocationDir}"\n')

    errorCreatingTarFile = False

    if "-t" in flashTestOpts and "-vv" not in flashTestOpts:
        log.stp("No archiving done for test-run. FlashTest complete. End of Logfile.")
        os.remove(os.path.join(pathToInvocationDir, ".lock"))
    elif "-t" in flashTestOpts and "-vv" in flashTestOpts:
        log.stp("No main archiving done for test-run.")
        os.remove(os.path.join(pathToInvocationDir, ".lock"))
    elif (not pathToMainArchive) and (not pathToViewArchive):
        log.stp("FlashTest complete. End of Logfile.")
        os.remove(os.path.join(pathToInvocationDir, ".lock"))
    else:
        log.stp(
            "Preparing data for archiving. Outcome of archiving attempt will be written to\n"
            + '"%s"\n' % os.path.join(pathToSiteDir, "archive.log")
            + "and will be incorporated into the regular logfile of the next invocation.\n"
            + "End of Logfile."
        )

        # instantiate archive logfile - this data will appear
        # in the next invocation's regular logfile
        archiveLog = Logfile(pathToSiteDir, "archive.log", "-v" in flashTestOpts)
        archiveLog.info("Archiving results for invocation %s:" % invocationDir, False)

        try:
            # file already removed
            os.remove(os.path.join(pathToInvocationDir, ".lock"))
        except OSError as e:
            if e.errno != os.errno.ENOENT:
                raise OSError(e)

        if pathToMainArchive:
            archiveLog.stp(
                'Creating local tarball "%s.tar.gz" for main archive...'
                % pathToInvocationDir
            )
            try:
                pathToTarFile = arch.makeTarFile()
            except Exception as e:
                errorCreatingTarFile = True
                archiveLog.err(
                    "Error creating tarball\n%s\n" % e
                    + "No files will be deleted from local copy."
                )
            else:
                try:
                    arch.sendTarFileToMainArchive(pathToTarFile)
                except Exception as e:
                    archiveLog.err(
                        "Unable to send tarball to main archive\n%s\n" % e
                        + 'Tarfile still exists at "%s"' % pathToTarFile
                    )
                else:
                    archiveLog.stp("Tarball sent to main archive.")
                    # remove local copy of tarball
                    os.remove(pathToTarFile)

                archiveLog.stp("Deleting specified files for slim copy...")
                # the files "deleted_files" that this method generates will obviously
                # only be present in the copy of the output sent to the view archive
                __deleteFiles(pathToInvocationDir)
                archiveLog.stp("Local files deleted.")
            log = archiveLog    # below this point, appending to log means appending to archive.log,
                                # if we have started using that.

    if ("-vv" in flashTestOpts or "-t" not in flashTestOpts):
        if pathToViewArchive:
            if "-vv" in flashTestOpts and "-t" not in flashTestOpts:
                log.stp("Finishing output to view archive...")
            elif "-t" in flashTestOpts or not pathToMainArchive or errorCreatingTarFile:
                log.stp("Sending fat copy of output to view archive...")
            else:
                log.stp("Sending slim copy of output to view archive...")

            try:
                open(os.path.join(pathToInvocationDir, ".lock"), "w").write("")
                arch.sendToViewArchive("-vv" in flashTestOpts and "-t" not in flashTestOpts)
            except Exception as e:
                log.err("%s\n" % e + "No copy of output sent to view archive.")
            else:
                if "-t" in flashTestOpts or not pathToMainArchive or errorCreatingTarFile:
                    log.stp("Fat copy of output sent to view archive.")
                else:
                    log.stp("Slim copy of output sent to view archive.")

            os.remove(os.path.join(pathToInvocationDir, ".lock"))

        log.stp("FlashTest complete.")

    pidFile.unregisterPid(pathToPidFile)


def usage():
    print('Usage for "flashTest.py":')
    print("  ./flashTest.py [general opts] [test-path#1] [override opts] \\")
    print("                                [test-path#2] [override opts] \\")
    print("                                [test-path#n] [override opts]")
    print("or:")
    print("  ./flashTest.py [general opts] -f [path/to/job/file] \\")
    print("                                   [test-path#1][override opts]")
    print("")
    print("General options to FlashTest are:")
    print('-c <file>: use <file> as "config" instead of default')
    print('-i <file>: use <file> as source of "test.info" data')
    print('-f <file>: read <file> (a "job-file") for list of test-paths')
    print("-o <dir> : direct output to <dir>")
    print("-s <name>: <name> is the name of this site (host)")
    print('-e <file>: <file> is used as the "exeScript" instead of the default')
    print("-t       : test run (no archiving)")
    print("-u       : update FLASH before run")
    print("-v       : verbose output (print logfile as it is written)")
    print(
        "-vv      : send results to view archive incrementally (if -t is not used)"
    )
    print(
        "-vv -t   : view-archiving enabled (non-incremental), but no main-archiving"
    )
    print("-L       : send log files to log archive")
    print("-z <dir> : FLASH source rooted at <dir>")
    print(
        "--force  : Run test even if other instance(s) of flashTest currently running"
    )
    print("")
    print("Each option must be entered with its own preceding dash. For example")
    print("")
    print("  $ ./flashTest.py -t -v -f path/to/job/file")
    print("")
    print("will work, but")
    print("")
    print("  $ ./flashTest.py -tvf path/to/job/file")
    print("")
    print("will not.")
    print("")
    print("-i, -o, and -z options will override 'pathToInfo', 'pathToOutdir', and")
    print("'pathToFlash' in the \"config\" file.")
    print("")
    print('Variables that are set in the "config" file or in a "test.info" file')
    print("may be overridden on the command line, or in a job-file, by so-called")
    print('"override options" e.g.:')
    print("")
    print("  $ ./flashTest.py Comparison/Sod key1=val1 key2=val2")
    print("")
    print("If an option passed in this way, for example, 'key1', requires no value")
    print("the syntax looks like:")
    print("")
    print("  $ ./flashTest.py Comparison/Sod key1= key2=val2")
    print("")
    print("Different entryPoint, setupper, compiler, executer, and tester components")
    print('can be assigned to different test-species in the "config" file. See the')
    print('notes in "config" for more details or see the FlashTest User\'s Guide.')


if __name__ == "__main__":
    # add "lib" to our sys.path. It will be in the
    # same directory where the executable is found
    sys.path.insert(
        0, os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "lib")
    )
    import flashTestParser as parser
    from archive import Archive
    from getProcessResults import getProcessResults
    from layeredDict import LayeredDict
    from logfile import Logfile
    from testObject import TestObject
    from xmlNode import parseXml, parseXmlString
    import pidFile
    import remoteFile

    locale.setlocale(locale.LC_CTYPE, '')

    if len(sys.argv) == 1 or sys.argv[1] == "-h":
        usage()
    else:
        main()

