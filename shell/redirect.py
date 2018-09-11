#! /usr/bin/env python3

import os, sys, time, re

#Get input from user
commmandLine = input("Enter redirect command: \n")
type(commmandLine)

print()

#Check which redirect they want to do stdin/stdout
if (">" in commmandLine): #stdout
	parts = re.split(">", commmandLine)
	parts[1] = parts[1].strip()
	outputFname = parts[1]
	first = re.split(" ", parts[0])
	command = first[0]
	inputFname = first[1]

elif ("<" in commmandLine): #stdin
	parts = re.split("<", commmandLine)
	parts[1] = parts[1].strip()
	inputFname = parts[1]
	command = parts[0]
	command = command.replace(" ", "")
	command = command.strip()
	outputFname = "theScreen"	

#print out the command entered in pieces to make sure it's seperated correctly
print("Executing command: " + command)  
print("Reading input from: " + inputFname) 
print("Writing output to: " + outputFname + "\n")

pid = os.getpid()               # get and remember pid

os.write(1, ("About to fork (pid=%d)\n" % pid).encode())

rc = os.fork()

if rc < 0:
    os.write(2, ("fork failed, returning %d\n" % rc).encode())
    sys.exit(1)

elif rc == 0:                   # child
    os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 (os.getpid(), pid)).encode())
    args = [command, inputFname]

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
