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


def unregisterPid(pidFile):
                print("trying to delete:", pidFile)
                pid=os.getpid()
                try:
                        #Open file, obtain lock and remove if this flashTest owns it
                        #This will block. Not sure O_EXCL is not ignored
                        fd= os.open(pidFile, os.O_RDONLY|os.O_EXCL)
                        print(fd)
                        if lockFile(fd, False):
                                apid = os.read(fd,MAXPIDBYTE)
                                print(apid.strip())
                                apid=struct.unpack('>HHHH',apid)[0]
                                #print(type(pid), "new ", type(apid.strip()))
                                if str(pid) != apid:
                                        unlockFile(fd)
                                        os.close(fd)
                                        print("deleting finally")
                                        os.remove(pidFile)
                                else:
                                        print("else block")
                                        unlockFile(fd)
                                        os.close(fd)
                except Exception as e:
                                print("Unable to delete my own /tmp/flashTest.pid")
                                pass
def main():
    pidFile = "/tmp/flashTest.pid"
    unregisterPid(pidFile)
main()
