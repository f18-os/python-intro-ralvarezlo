#! /usr/bin/env python3
import sys, os, re, string, time
"""
Takes an string (previously splitted if there is a pipe sign) and returns
an array uIn such as [Command String, Input File (if exists)] or [Cpmmand String]
and uOut which is an string of the file where the output might be redirected
"""
def setIns(auxStr):
    auxIn = auxStr.split(" ")
    uIn = [auxIn[0]]
    out = ""
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
        elif len(auxIn) ==2:
            uIn.append(auxIn[1])
        i += 1
    return uIn, out
"""
Takes an string and splits it when the pipe symbol occurs,
it returns an array of string and a boolean to know if the input requires pipping
"""
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

"""
SET FILE DESCRIPTORS
toClose: 1 or 0 (The fileDescriptor that will be closed)
w, r: File descriptors opened by the pipe command to write and read respectively
"""
def setFds(toClose, w, r):
    os.close(toClose)
    # if we close #1 we know we will want to dup the writting fd
    if (toClose==1):
        #fd = w
        os.dup2(w, 1)
    else: 
        #fd = r
        os.dup2(r, 0)
    
    
    for pipefd in (r, w):
        os.close(pipefd)

    # sets the selected fd to inheritable
    
"""
Executes a command given the arguments (Given by the professor)
"""
def excIt(args):
    #Handle Redirect
    try:
        auxPath = args[1].split("\\")
        myPath= ""
        if (len(auxPath)>1):
            i =0
            while (i < len(auxPath)-1):
                myPath  = myPath + auxPath + "//"
            myPath = myPath[:len(auxPath)-2]
            changeDirectory(myPath)
    except: pass
    #Actual Excecution
    for dir in re.split(":", os.environ['PATH']): # try each directory in path
        programIn = "%s/%s" % (dir, args[0])
        try:
            os.execve(programIn, args, os.environ) # try to exec program
        except FileNotFoundError:             # ...expected
            pass

"""
Give the case that we want to redirect the output to an especific file
it takes the fileName and sets it as the 'new' stdout
"""
def setOutFile(uOut):
    if (uOut != ""):
        os.close(1)                 # redirect child's stdout
        sys.stdout = open(uOut, "w")
        fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
        os.set_inheritable(fd, True)

def changeDirectory(path):
    try:
        os.chdir(path)
    except:
        os.write(3, ("\nIncorrect location\n").encode())

def mainRun(auxStr):
    if (auxStr == "exit"): sys.exit(1)
    doPipe, myIns = mustPipe(auxStr)
    pid = os.getpid()
    if(doPipe):
        pr, pw = os.pipe()
        for fd in (pr, pw):
            os.set_inheritable(fd, True)

    fork1 = os.fork()
    if fork1 < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif fork1 == 0:                   # child1
        """
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                    (os.getpid(), pid)).encode())
                    """
        args, myOut = setIns(myIns[0])
        if doPipe:
            setFds(1, pw, pr)
        else:
            setOutFile(myOut)
        excIt(args)
    else:
        
        if doPipe:
            fork2 = os.fork()
            if fork2 < 0:
                os.write(2, ("fork failed, returning %d\n" % rc).encode())
                sys.exit(1)

            elif fork2 == 0:                   # child2
                args, myOut = setIns(myIns[1])
                setFds(0, pw, pr)
                #setOutFile(myOut)
                excIt(args) 
            else:
                childPidCode = os.wait()

                for pipefd in (pw, pr):
                    os.close(pipefd)
        child2Pid = os.wait()

 
done = False
while not done:
    try:
        if 'PS1' in os.environ:
            os.write(1, os.environ['PS1'].encode())
            auxStr = input("")
        else: auxStr = input("$ ")
        run = True
        if(auxStr==""): run = False #Handle enters
        if(auxStr[0:2]=="cd"):
            try:
                changeDirectory(auxStr[3:])
            except:
                print("Incorrect Path")
                pass
            run = False
        
    except EOFError: #catch ctr + D
        print("\n") #avoid the annoying shell log after close
        sys.exit(1)
    
    if(run):
        mainRun(auxStr)
    