#! /usr/bin/env python3

import os, sys, time, re

commmandLine = ''
#Get input from user
commmandLine = input()
#print()

if "|" in commmandLine:
	parts = commmandLine.split("|")
	first = parts[0].split(" ")
	command1 = first[0]
	inputFname = first[1]
	inputFname = inputFname.strip()
	command2 = parts[1].strip()
	outputFname = "theScreen"
	# print(command1)
	# print(inputFname)
	# print(command2)
	# print(outputFname)
	# print()

elif ">" in commmandLine:
	parts = commmandLine.split(">")
	first = parts[0].split(" ")
	command1 = first[0]
	inputFname = first[1]
	inputFname = inputFname.strip()
	outputFname = parts[1].strip()
	# print(command1)
	# print(inputFname)
	# print(outputFname)
	# print()

elif "<" in commmandLine:
	parts = commmandLine.split("<")
	command1 = parts[0]
	command1 = command1.strip()
	inputFname = parts[1].strip()
	outputFname = "theScreen"
	# print(command1)
	# print(inputFname)
	# print(outputFname)
	# print()
	
else:
	parts = commmandLine.split(" ")
	if len(parts) > 1:
		command1 = parts[0]
		inputFname = parts[1]
	else:
		command1 = parts[0]
		inputFname = ''
	outputFname = "theScreen"
	# print(command1)
	# print(inputFname)
	# print(outputFname)
	# print()

pid = os.getpid()               # get and remember pid

if "|" in commmandLine:

	pr,pw = os.pipe()
	for f in (pr, pw):
		os.set_inheritable(f, True)
	# print("pipe fds: pr=%d, pw=%d" % (pr, pw))

	import fileinput

	# print("About to fork (pid=%d)" % pid)

	rc = os.fork()

	if rc < 0:
		print("fork failed, returning %d\n" % rc, file=sys.stderr)
		sys.exit(1)

	elif rc == 0:                   #  child - will write to pipe
		# print("Child: My pid==%d.  Parent's pid=%d" % (os.getpid(), pid), file=sys.stderr)
		if ('' == inputFname):
			args = [command1]
		else:
			args = [command1, inputFname]
		#print(*args, sep = "\n")

		os.close(1)                 # redirect child's stdout
		os.dup(pw)
		for fd in (pr, pw):
			os.close(fd)
		fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
		os.set_inheritable(fd, True)
		# os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, args[0])
			try:
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
		sys.exit(1)    
    
	lc = os.fork()

	if lc < 0:
		print("fork failed, returning %d\n" % rc, file=sys.stderr)
		sys.exit(1)

	elif lc == 0:                   #  child - will write to pipe
		# print("Child: My pid==%d.  Parent's pid=%d" % (os.getpid(), pid), file=sys.stderr)
		args = [command2]
		# print(*args, sep = "\n")

		os.close(0)                 # redirect child's stdout
		os.dup(pr)
		for fd in (pr, pw):
			os.close(fd)
		fd = sys.stdin.fileno() # os.open("p4-output.txt", os.O_CREAT)
		os.set_inheritable(fd, True)
		# os.write(2, ("Child: opened fd=%d for reading\n" % fd).encode())

		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, args[0])
			try:
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
		sys.exit(1)             

	else:                           # parent (forked ok)
		# print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
		os.close(0)
		os.dup(pr)
		for fd in (pw, pr):
			os.close(fd)
		#for line in fileinput.input():
			#print("From child: <%s>" % line)
else:
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        # os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
                 # (os.getpid(), pid)).encode())
        if '' == inputFname:
        	args = [command1]
        else:
        	args = [command1, inputFname]

        #writes stdout to an output file
        if outputFname is not "theScreen":
            os.close(1)                 # redirect child's stdout
            sys.stdout = open(outputFname, "w")
            fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
            os.set_inheritable(fd, True)
            # os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

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
            # os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)
    else:                           # parent (forked ok)
        # os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
                 # (pid, rc)).encode())
        childPidCode = os.wait()
        # os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
        #          childPidCode).encode())
