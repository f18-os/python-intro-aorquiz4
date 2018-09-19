#! /usr/bin/env python3

import os, sys, time, re

#Get input from user
commmandLine = input("Enter command: \n$ ")

type(commmandLine)

print()

if ("|" in commmandLine):
    processes = commmandLine.split("|")
    process1 = processes[0].split()
    process2 = processes[1].split()
    print(process1)
    print(process2)
    print()
    if ("<" in process1):
        process1.remove("<")
    if ("<" in process2):
        process2.remove("<")
    if (">" in process2):
        outputFname = process2[2] 
    else:
        outputFname = "theScreen"
    print(process1)
    print(process2) 
    print()  
else:
    process1 = commmandLine.split()
    print(process1)
    if ("<" in process1):
        process1.remove("<")
    if (">" in process1):
        process1.remove(">")
        outputFname = process1[2]
    else:
        outputFname = "theScreen"
    print(process1)
    print()

print(commmandLine)


#print to make sure all commands and files are noted for
if ("|" in commmandLine):
    #print out the command entered in pieces to make sure it's seperated correctly
    print("Executing first command: " + process1[0])  
    print("Reading input from: " + process1[1])
    print("Executing second command: " + process2[0])
    if (">" in commmandLine): 
        print("Writing output to: " + process2[2])
    else:
        print("Writing output to: The Screen")
    print()
else:
    print("Executing first command: " + process1[0])
    print("Reading input from: " + process1[1])
    if (">" in commmandLine):
        print("Writing output to: " + outputFname)
    else:
        print("Writing output to: The Screen")
    print()


pid = os.getpid()               # get and remember pid

os.write(1, ("About to fork (pid=%d)\n" % pid).encode())

if("|" in commmandLine):
    print("We're going piping boys!!!")
    r,w = os.pipe()

    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 (os.getpid(), pid)).encode())
        args1 = [process1[0], process1[1]]
        if (len(process2) == 2):
            args2 = [process2[0], process2[2]]
        else:
            args2 = [process2[0]]

        os.close(r)
        w = os.fdopen(w, "w")
        print("child writing to pipe")
        fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
        os.set_inheritable(fd, True)
        os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
        for dir in re.split(":", os.environ['PATH']): # try each directory in path
            program = "%s/%s" % (dir, args1[0])
            try:
                os.execve(program, args1, os.environ) # try to exec program
            except FileNotFoundError:             # ...expected
                pass                              # ...fail quietly 

        os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    #second process after pipe
    lc = os.fork()

    if lc < 0:
        os.write(2, ("fork failed, returning %d\n" % lc).encode())
        sys.exit(1)

    elif lc == 0:
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 (os.getpid(), pid)).encode())

        os.close(1)
        os.dup(w)
        args2 = [process2[0]]
        
        print("child Reading from pipe")


        #writes stdout to an output file
        if outputFname is not "theScreen":
            os.close(1)                 # redirect child's stdout
            sys.stdout = open(outputFname, "w")
            fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
            os.set_inheritable(fd, True)
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args2[0])
                try:
                    os.execve(program, args2, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error
        #prints the stdin
        elif outputFname is "theScreen":
            fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args2[0])
                try:
                    os.execve(program, args2, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)
        else:                           # parent (forked ok)
            os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                    (pid, rc)).encode())
            childPidCode = os.wait()
            os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                    childPidCode).encode())
       
else:
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 (os.getpid(), pid)).encode())
        args = [process1[0], process1[1]]

        #writes stdout to an output file
        if outputFname is not "theScreen":
            os.close(1)                 # redirect child's stdout
            sys.stdout = open(outputFname, "w")
            fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
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
        #prints the stdin
        elif outputFname is "theScreen":
            fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)
    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                 (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                 childPidCode).encode())
