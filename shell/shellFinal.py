#! /usr/bin/env python3

import os, sys, time, re

def pipe_func(args, pipePos):
	pid = os.getpid()# get and remember pid
	pr,pw = os.pipe()
	for f in (pr, pw):
		os.set_inheritable(f, True)

	import fileinput

	rc = os.fork()

	if rc < 0:
		print("fork failed, returning %d\n" % rc, file=sys.stderr)
		sys.exit(1)

	elif rc == 0:                   #  child - will write to pipe
		
		if (pipePos == 1):
			args1 = [args[0]]
		elif (pipePos == 2):
			args1 = [args[0], args[1]]

		os.close(1)                 # redirect child's stdout
		os.dup(pw)
		for fd in (pr, pw):
			os.close(fd)
		fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
		os.set_inheritable(fd, True)
		try:
			os.execve(args1[0], args1, os.environ) # try to exec program
		except FileNotFoundError:
			pass
		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, args1[0])
			try:
				os.execve(program, args1, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		os.write(2, ("Child:    Error: Could not exec %s\n" % args1[0]).encode())
		sys.exit(1)    
    
	lc = os.fork()

	if lc < 0:
		print("fork failed, returning %d\n" % rc, file=sys.stderr)
		sys.exit(1)

	elif lc == 0:                   #  child - will write to pipe
		
		if (pipePos == 1) and (len(args) == 4):
			args2 = [args[2], args[3]]
		elif (pipePos == 2) and (len(args) == 5):
			args2 = [args[3], args[4]]
		elif (pipePos == 2) and (len(args) == 4):
			args2 = [args[3]]
		elif len(args) == 3:
			args2 = [args[2]]

		os.close(0)                 # redirect child's stdout
		os.dup(pr)
		for fd in (pr, pw):
			os.close(fd)
		fd = sys.stdin.fileno() # os.open("p4-output.txt", os.O_CREAT)
		os.set_inheritable(fd, True)

		try:
			os.execve(args2[0], args2, os.environ) # try to exec program
		except FileNotFoundError:
			pass

		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, args2[0])
			try:
				os.execve(program, args2, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		os.write(2, ("Child:    Error: Could not exec %s\n" % args2[0]).encode())
		sys.exit(1)             

	else:                           # parent (forked ok)
		os.dup(pr)
		for fd in (pw, pr):
			os.close(fd)
		#for line in fileinput.input():
			#print("From child: <%s>" % line)

def red_func(args, redPos, redirectSym):
	pid = os.getpid()# get and remember pid
	pr,pw = os.pipe()
	for f in (pr, pw):
		os.set_inheritable(f, True)

	rc = os.fork()

	if rc < 0:
		print("fork failed, returning %d\n" % rc, file=sys.stderr)
		sys.exit(1)

	elif rc == 0:
		if redirectSym == ">":
			outputFname = args[args.index('>')+1]
			args1 = args[0:args.index('>')]

			os.close(1)                 # redirect child's stdout
			sys.stdout = open(outputFname, "w")
			fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
			os.set_inheritable(fd, True)
			# os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

			try:
				os.execve(args1[0], args1, os.environ) # try to exec program
			except FileNotFoundError:
				pass

			for dir in re.split(":", os.environ['PATH']): # try each directory in path
				program = "%s/%s" % (dir, args1[0])
				try:
					os.execve(program, args1, os.environ) # try to exec program
				except FileNotFoundError:             # ...expected
					pass                              # ...fail quietly 

			os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
			sys.exit(1)                 # terminate with error
		#prints the stdin
		elif redirectSym == "<":
			del args[1]

			fd = sys.stdout.fileno() # os.open(outputFname, os.O_CREAT)
			# os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

			try:
				os.execve(args[0], args, os.environ) # try to exec program
			except FileNotFoundError:
				pass

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

def single_command(args):
	pid = os.getpid()               # get and remember pid

	# os.write(1, ("About to fork (pid=%d)\n" % pid).encode())

	rc = os.fork()

	if rc < 0:
		os.write(2, ("fork failed, returning %d\n" % rc).encode())
		sys.exit(1)
	elif rc == 0:
		# os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
		# 		 (os.getpid(), pid)).encode())

		fd = sys.stdout.fileno()
		os.set_inheritable(fd, True)
		# os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())

		try:
			os.execve(args[0], args, os.environ) # try to exec program
		except FileNotFoundError:
			pass

		if "/" in args:
			os.execve(args[0], args, os.environ)

		for dir in re.split(":", os.environ['PATH']): # try each directory in path
			program = "%s/%s" % (dir, args[0])
			try:
				os.execve(program, args, os.environ) # try to exec program
			except FileNotFoundError:             # ...expected
				pass                              # ...fail quietly 

		os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
		sys.exit(1)                 # terminate with error

	else:                           # parent (forked ok)
		# os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
		# 		 (pid, rc)).encode())
		childPidCode = os.wait()
		# os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
		# 		 childPidCode).encode())

while True:
	#Get input from user
	if 'PS1' in os.environ:
		os.write(1, os.environ['PS1'].encode())

	try:
		commmandLine = input()
	except EOFError:
		sys.exit(1)
	except ValueError:
		sys.exit(1)

	if " " in commmandLine:
		args = commmandLine.split(" ")
	else:
		args = [commmandLine]

	#handle pipe
	if "|" in args:
		if len(args) == 4:
			if "|" in args[1]:
				pipe_func(args, 1)
			elif "|" in args[2]:
				pipe_func(args, 2)
		elif len(args) == 3:
			if "|" in args[1]:
				pipe_func(args, 1)
		elif len(args) == 5:
				pipe_func(args, 2)

	#handle redirect in
	elif "<" in args:
		if len(args) == 3:
			red_func(args, 1, "<")

	#redirect output
	elif ">" in args:
		if len(args) == 4:
			red_func(args, 2, ">")
		elif len(args) == 3:
			red_func(args, 1, ">")
	elif "cd" in args[0]:
		try:
			os.chdir(args[1])
		except FileNotFoundError:
			pass

	#handle single command
	elif '' != commmandLine:
		single_command(args) 

