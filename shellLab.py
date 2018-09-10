import sys
import os
import subprocess
import string

uExit = False
uForkInt = 1


while not uExit and (uForkInt>=0):
    print("staring loop")
    uAns = input("myShell > ")
    uArgs = uAns.split(" ")
    
    if uArgs[0] == "wc":
        print("executing " + uArgs[0])
    elif uArgs[0] == "cd":
        if not 1<len(uArgs)<3:
            print("Incomplete instruction format should be cd <arg>")
        else:
            print("going to " + uArgs[1])
            pDir = os.getcwd
            os.chdir(os.path.expanduser(uArgs[1]))
            print("Your path is now " + string(os.getcwd))
    elif uArgs[0] == "pwd":
        print("Whatever that means")
    elif uArgs[0] == "exit":
        print("Exiting shell.")
        uExit = True
    else: print("Incorrect instruction (Supported instruction include: wc, cd, pwd & exit")


