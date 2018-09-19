#! /usr/bin/env python3
import sys, os, re, string, time

def setIns(auxStr):
    auxIn = auxStr.split(" ")
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

def mustPipe(auxStr):
    isPipe = False
    auxA = auxStr.split("|")
    if len(auxA) > 1:
        isPipe = True
        i = 1
        while i < len(auxA):
            if (auxA[i][0] == " "):
                auxA[i] = auxA[i][1:]
            length = len(auxA)-1
            if (auxA[i][length]==" "):
                length -= 1
                auxA[i] = auxA[i][:length]
            i +=1
    return isPipe, auxA

def setFds(toClose, w, r):
    os.close(toClose)
    os.write(2,("\nTo Close: %d \n" % toClose).encode())
    if (toClose==1):
        fd = w
    else: fd = r
    os.dup(fd)
    os.write(2,("FD: %d \n" % fd).encode())
    for a in (r, w):
        os.close(a)
    if (toClose == 1):
        fdc = sys.stdout.fileno()
    else:
        fdc = sys.stdin.fileno()
    os.set_inheritable(fdc, True)
    os.write(2, ("\nStd o.i = %d" % fdc).encode())
    

def excIt(args):
    os.write(2, ("\nArgs0 is: :"+ args[0]+ ":").encode())
    lenght = len(args)
    os.write(2, ("\nArgsLength is: %d" % lenght).encode())
    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        programIn = "%s/%s" % (dir, args[0])
        try:
            os.execve(programIn, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass

def setOutFile(uOut):
    if (uOut != "p4-output.txt"):
        print("output is " + uOut)
        os.close(1)                 # redirect child's stdout
        sys.stdout = open(1, "w")
        fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
        os.set_inheritable(fd, True)
        os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())


done = False
pr, pw = os.pipe()
while not done:
    auxStr = input("$ ")
    if (auxStr == "exit"): sys.exit(1)
    doPipe, myIns = mustPipe(auxStr)
    pid = os.getpid()
        

    fork1 = os.fork()
    if fork1 < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif fork1 == 0:                   # child1
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                    (os.getpid(), pid)).encode())

        args, myOut = setIns(myIns[0])
        if doPipe:
            setFds(1, pw, pr)
        else:
            setOutFile(myOut)

        excIt(args)
    else:
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                 (pid, fork1)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                 childPidCode).encode())
        if doPipe:
            fork2 = os.fork()
            if fork2 < 0:
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)

            elif fork2 == 0:                   # child1
                os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                            (os.getpid(), pid)).encode())
                args, myOut = setIns(myIns[1])
                os.write(1, ("\nArgs: " +  args[0]).encode())
                setFds(0, pw, pr)
                setOutFile(myOut)
                excIt(args) 
            else:
                os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                        (pid, fork2)).encode())
                childPidCode = os.wait()
                os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                        childPidCode).encode())