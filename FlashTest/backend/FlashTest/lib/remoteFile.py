import tempfile
import subprocess
import time
import uuid
import os,sys

sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))

def _run(args, input=None):
  p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout, stderr = p.communicate(input)
  if p.returncode != 0: raise Exception(subprocess.list2cmdline(args) + ':\n' + stderr)
  return stdout

def splitHostAndPath(path):
  if path.count(':') > 0:
    x = path.split(':', 1)
    return (x[0] or 'localhost', x[1])
  else:
    return ('localhost', path)

# returns contents of file as string
def readfile(path):
  host, path = splitHostAndPath(path)
  if host != 'localhost':
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    tmp = tmp.name
    try:
      _run(['scp','%s:%s'%(host,path),tmp])
      with open(tmp) as f:
        data = f.read()
    finally:
      os.remove(tmp)
  else:
    with open(path) as f:
      data = f.read()
  return data

# writes contents of file given string
def writefile(path, data):
  host, path = splitHostAndPath(path)
  if host != 'localhost':
    w = tempfile.NamedTemporaryFile(delete=False)
    w.write(data)
    w.close()
    w = w.name
    try:
      _run(['scp',w,'%s:%s'%(host,path)])
    finally:
      os.remove(w)
  else:
    with open(path,'w') as w:
      w.write(data)

# delta: string -> string
def updatefile(path, delta):
  def mv(src,dst): # move (hopefully atomically) a file from src to dst
    shost, spath = splitHostAndPath(src)
    dhost, dpath = splitHostAndPath(dst)
    if shost != dhost: raise ValueError('cannot move files on different hosts')
    if shost != 'localhost':
      _run(['ssh', shost, subprocess.list2cmdline(['mv',spath,dpath])])
    else:
      os.rename(spath, dpath)
  held = path + ".lock-" + uuid.uuid4().hex
  attempts = 0
  max_attempts = 5
  while attempts < max_attempts:
    try:
      mv(path, held)
      break
    except Exception as e:
      attempts += 1
      if attempts == max_attempts:
        raise Exception('Could not obtain lock on file %s:\n%s' % (path,str(e)))
      time.sleep(attempts) # wait 'attempts' number of seconds
  try: # we've got the file on hold: read it, change it, write it
    data = readfile(held)
    data = delta(data)
    writefile(held, data)
  finally:
    try: # and release the lock
      mv(held, path)
    except Exception as e:
      raise Exception('Could not release lock on file %s:\n' % (held,str(e)))

