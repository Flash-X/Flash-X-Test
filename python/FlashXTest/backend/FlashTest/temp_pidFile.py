#!/usr/bin/env python3

import os, errno, os.path
from fcntl import LOCK_UN, LOCK_EX,LOCK_NB, flock
import six
import struct
#MAXPIDBYTE=struct.calcsize("P")
MAXPIDBYTE=8
MAXPID=65536


def lockFile(fd,nonBlock=True):
        try:
                if nonBlock:
                        flock(fd,LOCK_EX|LOCK_NB)
                else:
                        flock(fd,LOCK_EX)
        except Exception as e:
                return False
        return True

def unlockFile(fd):
        flock(fd, LOCK_UN)

def registerPid(pidFile, forceRun=False):
        pid = os.getpid()
        try:
                fd=os.open(pidFile, os.O_CREAT|os.O_WRONLY|os.O_EXCL)
                if lockFile(fd):
                        os.write(fd, bytes(pid))
                        unlockFile(fd)
                        os.close(fd)
                        return True
        except OSError as e:
                if e.errno == errno.EEXIST:
                        #read pid from existing file
                        try:
                                fd=os.open(pidFile, os.O_RDWR|os.O_EXCL|os.O_NONBLOCK)
                                if lockFile(fd):
                                        os.lseek(fd,0,0)
                                        opid=os.read(fd,MAXPIDBYTE)

                                        #Check if opid is currently running process
                                        #otherwise no other instance is running, write current pid
                                        #to the file and return True
                                        try:
                                                if opid.strip() == "":
                                                        opid = MAXPID + 1
                                                else:
                                                        opid = opid

                                                os.kill( int.from_bytes(opid, byteorder='big'),0)
                                                #os.kill(int(codecs.encode(opid, 'hex'), 16),0)
                                                #os.kill(struct.unpack(">i", opid)[0])
                                        except OSError as e:
                                                if e.errno == errno.ESRCH:
                                                        os.ftruncate(fd,0)
                                                        os.lseek(fd,0,0)
                                                        spid=str(pid)
                                                        os.write(fd, spid)
                                                        unlockFile(fd)
                                                        os.close(fd)
                                                        return True
                                                else:
                                                        raise OSError(e)



                                #Else another flashTest process is running or has locked pidFile
                        except OSError as e:
                                #file has been opened by another process
                                if e.errno == errno.EBUSY:
                                        return forceRun
                                elif e.errno == errno.EACCES:
                                        return forceRun
                                else:
                                        raise OSError(e)

                        finally:
                                try:
                                        os.close(fd)
                                except:
                                        pass

        return forceRun

def unregisterPid(pidFile):
                pid=os.getpid()
                try:
                        #Open file, obtain lock and remove if this flashTest owns it
                        #This will block. Not sure O_EXCL is not ignored
                        fd= os.open(pidFile, os.O_RDONLY|os.O_EXCL)
                        if lockFile(fd, False):
                                apid = os.read(fd,MAXPIDBYTE)
                                if str(pid) == apid.strip():
                                        unlockFile(fd)
                                        os.close(fd)
                                        os.remove(pidFile)
                                else:
                                        unlockFile(fd)
                                        os.close(fd)
                except Exception as e:
                                pass

