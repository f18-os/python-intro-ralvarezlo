#! /usr/bin/env python3
import sys
import os
import re
import string
import time
import subprocess
import fileinput

def setIns(auxIn):
    uIn = [auxIn[0]]
    out = "p4-output.txt"

    i = 1
    while i < len(auxIn):
        if auxIn[i] == ">":
            if i+1 < len(auxIn):
                out = auxIn[i+1]
            if (i-1) != 0:
                uIn.append(auxIn[i-1])
        elif auxIn[i] == "<":
            if i+1 < len(auxIn):
                uIn.append(auxIn[i+1])
            if (i-1) != 0:
                out = auxIn[i-1]
            else:
                print("Invalid Argument")
                sys.exit(1)
        i += 1
    return uIn, out

def mustPipe (auxStr):
    isPipe = False
    auxArr = auxStr.split("|")
    if len(auxArr) > 1:
        isPipe = True
    return isPipe, auxArr

auxStr = input("$ ")
iPipe, auxArr = mustPipe(auxStr)
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

    if iPipe:
        r,w = os.pipe()
        # FIX THIS

        pid = os.getpid()               # get and remember pid
        os.write(1, ("About to fork for pipe (pid=%d)\n" % pid).encode())

        for f in (r,w):
            os.set_inheritable(f, True)
        fNum = os.fork()

        if fNum == 0: # child for pipe
            args, uOut = setIns(auxArr[0])
            os.close(1)
            
            os.dup2(w, 1, True)
            sys.stdout = open(w, 'w')
            for fd in (r, w):
                os.close(fd)
            
            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                programIn = "%s/%s" % (dir, args[0])
                try:
                    os.execve(programIn, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass
            sys.exit(1)
            
        else:
            args, uOut = setIns(auxArr[1])
            os.close(0)
            os.dup2(r, 0, True)
            for fd in (w, r):
                os.close(fd)
        
            auxStr = ""
            for line in fileinput.input():
                auxStr += line + "\n"
            args.append(auxStr)

            if (uOut != "p4-output.txt"):
                print("output is " + uOut)
                os.close(1)                 # redirect child's stdout
                sys.stdout = open(1, "w")
                fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
                os.set_inheritable(fd, True)
                os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            
            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                    sys.exit(1)
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error

    args, uOut = setIns(myIn)
    
    if (uOut != "p4-output.txt"):
        print("output is " + uOut)
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

