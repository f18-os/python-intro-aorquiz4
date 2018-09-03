#! /usr/bin/env python3

import sys        # command line arguments
import re         # regular expression tools
import os         # checking if file exists
import subprocess # executing program

# set input and output files
if len(sys.argv) is not 3:
    print("Correct usage: wordCount.py <input text file> <output file>")
    exit()

textFname = sys.argv[1]
outputFname = sys.argv[2]

#first check to make sure program exists
if not os.path.exists("wordCount.py"):
    print ("wordCount.py doesn't exist! Exiting")
    exit()

#make sure text files exist
if not os.path.exists(textFname):
    print ("text file input %s doesn't exist! Exiting" % textFname)
    exit()

#make sure output file exists
if not os.path.exists(outputFname):
    print ("wordCount output file %s doesn't exist! Exiting" % outputFname)
    exit()

#master dictionary
master = {}

#read text file
with open(textFname, 'r') as textFile:
	for lin in textFile:
        #convert to lower case
		lin = lin.lower()

		#get rid of new line char
		lin = lin.strip()

		#remove punctutation
		lin = re.sub(r'[^\w\s]',' ',lin)

		#split line into words
		wrds = re.split('[ \t]', lin)
		for w in wrds:
			#insert into dictionary if word is not in there. If it's not set words value to one
			if w in master:
				master[w] = master[w] + 1
			else:
				master[w] = 1

#removes '' from dictionary. Not sure how it's been added into the dictionary.
master.pop('', None)

#write to output file
with open(outputFname, "w") as outFile:
	#sort by key
	for key,val in sorted(master.items()):
		#for every key write in output file key and value
		outFile.write("%s %s\n" % (key, val))
