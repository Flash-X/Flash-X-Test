import sys, os, locale
from time import strftime, localtime

class Logfile:

  indentLen = 9

  def __init__(self, outdir, logfileName, verbose=False):
    self.outdir = outdir
    self.logfile = os.path.join(self.outdir, logfileName)
    self.verbose = verbose

    if os.path.exists(self.logfile):
      # make sure we start with a blank logfile
      os.remove(self.logfile)

  def info(self, msg, indent=True):
    self.__msg(msg, False, indent)

  def stp(self, msg):
    self.__msg(msg, True)

  def note(self, msg):
    self.__msg("NOTE!    " + msg)

  def warn(self, msg):
    self.__msg("WARNING: " + msg)

  def err(self, msg):
    self.__msg("ERROR:   " + msg)

  def brk(self):
    self.__msg("-"*80)

  def __msg(self, msg, stp=False, indent=False):
    """
    Write 'msg' to logfile after prepending timestamp (if 'stp' is True)
    """
    if stp:
      msg = "%s %s" % (strftime("%H:%M:%S", localtime()), msg)

    try:
      lines = msg.strip().split("\n")
    except:
      lines = msg.decode(encoding=locale.getpreferredencoding(False),errors="replace").strip().split("\n")
    for i in range(len(lines)):
      if i==0 and indent==False:
        continue
      else:
        lines[i] = " " * self.indentLen + lines[i]

    msg = "\n".join(lines)

    if self.verbose:
      # stdout is redirected to "test_output" in the
      # testing phase, so temporarily override this
      stdout = sys.stdout
      sys.stdout = sys.__stdout__
      print(msg)
      sys.stdout = stdout

    if not msg.endswith("\n"):
      msg = msg + "\n"

    open(self.logfile, "a").write(msg)

class ConsoleLog:

  indentLen = 5

  def __init__(self):
    pass

  def info(self, msg, indent=True):
    self.__msg(msg, False, indent)

  def stp(self, msg):
    self.__msg(msg, True)

  def note(self, msg):
    self.__msg("[flashxtest-note]:  " + msg)

  def warn(self, msg):
    self.__msg("[flashxtest-warn]:  " + msg)

  def err(self, msg):
    self.__msg("[flashxtest-error]: " + msg)

  def brk(self):
    self.__msg("-"*80)

  def __msg(self, msg, stp=False, indent=False):
    """
    Write 'msg' to logfile after prepending timestamp (if 'stp' is True)
    """
    if stp:
      msg = "%s %s" % (strftime("%H:%M:%S", localtime()), msg)

    lines = msg.strip().split("\n")
    for i in range(len(lines)):
      if i==0 and indent==False:
        continue
      else:
        lines[i] = " " * self.indentLen + lines[i]

    msg = "\n".join(lines)

    # stdout is redirected to "test_output" in the
    # testing phase, so temporarily override this
    stdout = sys.stdout
    sys.stdout = sys.__stdout__
    print(msg)
    sys.stdout = stdout
