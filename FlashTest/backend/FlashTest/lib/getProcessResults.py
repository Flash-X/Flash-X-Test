
import sys, os, time, signal, locale

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

CHUNKSIZE = 100               # number of bytes to read (default, for usePty)

def getProcessResults(cmd, timeout=None, usePty=False):
  cmd = cmd.strip()
  cmds = cmd.split(";")
  if len(cmds) == 1:
    return getProcessResultsInner(cmd, timeout, usePty)
  # else
  cmds = [cmd.strip() for cmd in cmds if len(cmd.strip()) > 0]
  combinedOut = ""
  combinedErr = ""
  combinedDur = ""
  for cmd in cmds:
    label = "for cmd = \"%s\":\n%s" % (cmd, "************" + "*" * len(cmd) + "\n")
    combinedOut += label
    combinedErr += label
    combinedDur += label

    out, err, dur, exitStatus = getProcessResultsInner(cmd, timeout, usePty)
    combinedOut += out + "\n"
    combinedErr += err + "\n"
    combinedDur += str(dur) + "\n"
    if exitStatus != 0:
      break

  # hack warning - if user is expecting duration to be
  # expressed as a float, as it is in the single 'cmd'
  # version, he'll be disappointed that 'combinedDur'
  # is a string.
  return (combinedOut, combinedErr, combinedDur, exitStatus)

def getProcessResultsInner(cmd, timeout=None, usePty=False):
  """
  executes 'cmd' in a separate process and returns a tuple
  containing the child's stdout and stderr together, the stderr
  separately, the duration of execution, and the process exit
  status. May use pseudo-terminals, perhaps to capture output of
  child process without buffering. Parent will abort the child if
  child fails to produce output for 'timeout' consecutive seconds.

  The command should be a string containing a valid shell command
  *without* any quoted space characters or other special characters
  embedded in the command or in arguments, since these may not be
  parsed as intended.
  DO NOT USE THIS FUNCTION TO PROCESS COMMANDS OF UNTRUSTED ORIGIN.

  Many thanks go to Jess Balint of the Chicago python3 users' group
  for invaluable help in developing an erlier version of this code,
  in which the subprocess module was not used.
  The current version uses the subprocess module unless usePty=True
  is requested. It was originally tested with Python 2.7.9 and 3.7.6.
  """
  import subprocess, select, fcntl

  global CHUNKSIZE               # refers to the global variable. This may be too weird.

  if timeout == None:
    timeout = 10 * 60  # kill process if it produces
                      # no output for 5 minutes.
                      # This is being upped to 10 for now. -PR

  useOsIO = False
  useSubprocess = not usePty

  if useSubprocess:
      p = subprocess.Popen(cmd, shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           bufsize=0)
      (stdOutR, stdErrR, childPid) = (p.stdout, p.stderr, p.pid)
      # Python 3.5 ff. has os.set_blocking(fd,blocking); but some
      # testing has shown that explicitly setting the fd to O_NONBLOCK may not be
      # necessary for Python 3 anyway.
      fcntl.fcntl(stdOutR, fcntl.F_SETFL, os.O_NONBLOCK)
      fcntl.fcntl(stdErrR, fcntl.F_SETFL, os.O_NONBLOCK)
      CHUNKSIZE = 200 # This may not be the right number, maybe much
                      # larger is okay.  But a justification for reading
                      # only in small chunks, even though much larger
                      # ones can also work, is the following: we do not
                      # want to lose much output in case a process dies
                      # prematurely.
  else:
      useOsIO = True      # If not using the subprocess module, always
                          # use functions from os directly.
      # Use a pipe for the stderr, because it's not file-buffered,
      # and a pseudo-terminal for the stdout if usePty is True.
      (stdErrR, stdErrW) = os.pipe()
      if usePty:
          (stdOutR, stdOutW) = os.openpty()
      else:
          (stdOutR, stdOutW) = os.pipe()
      try:
          CHUNKSIZE = select.PIPE_BUF # This may not be the right number, maybe much larger is okay
      except:
          pass
      # os.fork() will return the child's pid to the parent and 'None' to the child
      childPid = os.fork()

  if childPid:  # this is the parent
    out = b""
    err = b""
    stdOutDone = False
    stdErrDone = False

    if useSubprocess:
      if useOsIO:    # In this combinations of flags, extract the
                     # underlying file descriptors from the stream
                     # objects and use them for further I/O
                     # operations; otherwise, the stream objects from
                     # the Popen object will be used directly to
                     # invoke higher-level methods for I/O operations.
        stdOutR =stdOutR.fileno()
        stdErrR =stdErrR.fileno()
    else:      # We are dealing with file descriptors, not file objects.
      # parent doesn't need this end (child does)
      os.close(stdErrW)
      os.close(stdOutW)

    startTime = time.time()
    wasAborted = False                  # will be set after SIGTERM has been sent
    wasAbortedHard = False              # will be set after SIGKILL (aka 9) has been sent
    readsAfterAbort = 0

    effectiveTimeout = timeout
    while 1:
      # wait for some results (with a possible timeout)
      (rl, wl, xl) = select.select([stdOutR, stdErrR], [], [stdOutR, stdErrR], effectiveTimeout)

      if len(rl) == 0 and not wasAborted:
        # we timed out, so kill the child (gently)
        if useSubprocess: p.send_signal(signal.SIGTERM)
        else:             os.kill(childPid, signal.SIGTERM)
        emsg = "\nProcess killed (-TERM) by FlashTest after producing no output for %s seconds.\n" % effectiveTimeout
        err += emsg.encode()
        effectiveTimeout = max(1, timeout / 20)
        wasAborted = True
        continue

      elif wasAborted and (len(rl) == 0 or readsAfterAbort >= 10):
        # we timed out, so kill the child (vigorously)
        if useSubprocess: p.kill()
        else:             os.kill(childPid, 9)
        if len(rl) == 0: emsg = "\nProcess killed (-9) by FlashTest after producing no output for another %s seconds.\n" % effectiveTimeout
        else: emsg = "\nProcess provided output %d times after being killed.\n" % readsAfterAbort
        err += emsg.encode()
        wasAbortedHard = True
        break

      # else
      if stdOutR in rl:
        try:
          # capture the output of the child. Pseudo-terminals sometimes replace
          # regular newlines '\n' with '\r\n', so replace all instances of '\r'
          # with the empty string. This behavior of pseudo-terminals makes them
          # unsafe for use when the child's output is binary data.
          if usePty:
            o = os.read(stdOutR, CHUNKSIZE).replace(b"\r",b"")
          else:
            if useOsIO:
              o = os.read(stdOutR, CHUNKSIZE)
            else:
              o = stdOutR.read(CHUNKSIZE)
          if wasAborted: readsAfterAbort += 1
        except OSError:
          # we might not be able to read the pty, so we trap the error and set
          # 'end' to True. We don't break because there might be something yet
          # to read from 'stdErrR'.
          stdOutDone = True
        else:
          try:
            len_o = len(o)
            if len_o:
              try:
                out += o
                len_out = len(out)
              except MemoryError as ex:
                o = b""
                out = b""
                out = ("***Memory Error, discarding standard output!***\n%s" % ex).encode(errors="ignore")
                stdOutDone = True
                # Something is badly wrong, so kill the child (try gently)
                if not wasAborted:
                  if useSubprocess: p.send_signal(signal.SIGTERM)
                  else:             os.kill(childPid, signal.SIGTERM)
                  out += b"\nProcess killed (-TERM) by FlashTest because a MemoryError was caught.\n"
                  err += b"\nProcess killed (-TERM) by FlashTest because a MemoryError was caught.\n"
                  effectiveTimeout = max(1, timeout / 20)
                  wasAborted = True
                else:
                  # we already tried to terminate, so kill the child (vigorously)
                  if useSubprocess: p.kill()
                  else:             os.kill(childPid, 9)
                  out += b"\nProcess killed (-9) by FlashTest because a MemoryError was caught.\n"
                  err += b"\nProcess killed (-9) by FlashTest because a MemoryError was caught.\n"
                  wasAbortedHard = True
                  break
              else:
                if len_out > 10*1024*1024:
                # Something went probably wrong, too much output to stdout.
                  if not wasAborted:
                    if useSubprocess: p.send_signal(signal.SIGTERM)
                    else:             os.kill(childPid, signal.SIGTERM)
                    out += b"\nProcess killed (-TERM) by FlashTest, more than 10 MiB of standard output.\n"
                    err += b"\nProcess killed (-TERM) by FlashTest, more than 10 MiB of standard output.\n"
                    effectiveTimeout = max(1, timeout / 20)
                    wasAborted = True
                  else:
                    # we already tried to terminate, so kill the child (vigorously)
                    if useSubprocess: p.kill()
                    else:             os.kill(childPid, 9)
                    out += b"\nProcess killed (-9) by FlashTest, more than 10 MiB of standard output.\n"
                    err += b"\nProcess killed (-9) by FlashTest, more than 10 MiB of standard output.\n"
                    wasAbortedHard = True
                    break
            else: stdOutDone = True
          except SystemError as ex:
            o = b""
            out = b""
            out = ("***System Error (maybe a memory problem?), discarding standard output!***\n%s" % ex).encode(errors="ignore")
            stdOutDone = True
            # Something is badly wrong, so kill the child (try gently)
            if not wasAborted:
              if useSubprocess: p.send_signal(signal.SIGTERM)
              else:             os.kill(childPid, signal.SIGTERM)
              out += b"\nProcess killed (-TERM) by FlashTest because a SystemError was caught.\n"
              err += b"\nProcess killed (-TERM) by FlashTest because a SystemError was caught.\n"
              effectiveTimeout = max(1, timeout / 20)
              wasAborted = True
            else:
              # we already tried to terminate, so kill the child (vigorously)
              if useSubprocess: p.kill()
              else:             os.kill(childPid, 9)
              out += b"\nProcess killed (-9) by FlashTest because a SystemError was caught.\n"
              err += b"\nProcess killed (-9) by FlashTest because a SystemError was caught.\n"
              wasAbortedHard = True
              break

      if stdErrR in rl:
        # stdErr is a pipe, not a pseudo-terminal like stdOut, so we can read
        # from the stream without a try-except block, knowing that a pipe will
        # return the empty string on end-of-file instead of raising an exception
        if useOsIO:
          e = os.read(stdErrR, CHUNKSIZE)
        else:
          e = stdErrR.read(CHUNKSIZE)
        if e:
          if wasAborted: readsAfterAbort += 1
          # put error both in regular output stream and in its own
          out += e
          err += e
        else:
          # when the child process terminates gracefully on platforms
          # other than Irix, 'stdErrR' will appear in 'rl' and a call
          # to os.read() will return the empty string (sometimes)
          stdErrDone = True

      # when the child process terminates on Irix, it shows up
      # in the 'exceptional conditions' list returned by "select"
      if len(xl) > 0:
        break

      if stdOutDone and stdErrDone:
        # break only when both stdOut and stdErr streams are empty
        break

    endTime = time.time()
    duration = endTime - startTime
    if wasAbortedHard:
      exitStatus = 9
    else:
      try:
        if useSubprocess:
          exitStatus = p.wait()
        else:
          exitStatus = os.waitpid(childPid,0)[1]
      except:  # if 'childPid' no longer exists for some reason
        if wasAborted:
          exitStatus = 9
        else:
          exitStatus = "unknown"

    if useOsIO:
      os.close(stdErrR)
      os.close(stdOutR)
    else:      
      stdErrR.close()
      stdOutR.close()
    return (out.decode(encoding='utf-8',errors="ignore"),
            err.decode(encoding=locale.getpreferredencoding(False),errors="replace"),
            duration,
            exitStatus)

  else:  # this is the child

    # child doesn't need this end (parent does)
    os.close(stdErrR)
    os.close(stdOutR)

    # make sure we're clean
    sys.stdout.flush()
    sys.stderr.flush()

    # correct the new stdout and stderr
    os.dup2(stdOutW, sys.stdout.fileno())
    os.dup2(stdErrW, sys.stderr.fileno())

    # child doesn't need these either after they've been dup'd
    os.close(stdOutW)
    os.close(stdErrW)

    # Go
    cmd = cmd.split()
    try:
      os.execvp(cmd[0], cmd)
    except Exception as e:
      print (e)  # will go to duplicate of 'stdOutW'

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(2) # make sure child exits if execvp failed.

    # end of program. Nothing should happen after
    # 'exec' if the child has executed correctly.
