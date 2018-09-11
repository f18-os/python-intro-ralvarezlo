#! /usr/bin/env python3

import sys
import os
import re
import string
import time
import subprocess

def setIns(auxIn):
    uIn = list()
    out = "p4-output.txt"
    if len(auxIn) == 1:
        uIn = auxIn
    elif len(auxIn) == 2:
        uIn = auxIn
    elif len(auxIn) == 3:
        if auxIn[1] == "<":
            uIn[0] = auxIn[0]
            uIn[1] = auxIn[2]
        else:
            print("Incorrect input")
            sys.exit(1)
    elif len(auxIn) == 4:
        if auxIn[2] == ">":
            uIn[0] = auxIn[0]
            uIn[1] = auxIn[1]
            out = auxIn[3]
        elif auxIn[2] == "<":
            uIn[0] = auxIn[0]
            uIn[1] = auxIn[3]
            out = auxIn[1]
        else:
            print("Incorrect input")
            sys.exit(1)
    else: 
        print("no args")
        sys.exit(1)
    print("args are" + uIn[0])
    return uIn, out


auxStr = input("Please enter input: ")
print("string input is " + auxStr)
myIn = auxStr.split(" ")

pid = os.getpid()               # get and remember pid

os.write(1, ("About to fork (pid=%d)\n" % pid).encode())

rc = os.fork()

if rc < 0:
    os.write(2, ("fork failed, returning %d\n" % rc).encode())
    sys.exit(1)

elif rc == 0:                   # child
    os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 (os.getpid(), pid)).encode())
    # args = ["wc", "p3-exec.py"]
    args, uOut = setIns(myIn)

    for i in args:
        print("Args is " + i)
    print("out is " +  uOut)
    
    if (uOut != "p4-output.txt"):
        os.close(1)                 # redirect child's stdout
        sys.stdout = open(uOut, "w")
        fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
        os.set_inheritable(fd, True)
        os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass                              # ...fail quietly 

    os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
    sys.exit(1)                 # terminate with error

else:                           # parent (forked ok)
    os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                 (pid, rc)).encode())
    childPidCode = os.wait()
    os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                 childPidCode).encode())

