#! /usr/bin/env python3

import os, sys, time, re

def setIns():
    uIn = sys.argv
    out = "p4-output.txt"
    if len(sys.argv) == 1 or len(sys.argv) == 2:
        print("one or two commands")
    elif len(sys.argv) == 3:
        if sys.argv[1] == ">":
            uIn[0] = sys.argv[0]
            uIn[1] = sys.argv[2]
    elif len(sys.argv) == 4:
        if args[2] == ">":
            uIn[0] = sys.argv[0]
            uIn[1] = sys.argv[1]
            out = sys.argv[3]
        elif args[2] == "<":
            uIn[0] = sys.argv[0]
            uIn[1] = sys.argv[3]
            out = sys.argv[1]
        else: sys.exit(1)
    else: sys.exit(1)
    return uIn, out

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
    args, uOut = setIns()

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

