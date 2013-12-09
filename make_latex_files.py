#!/usr/bin/env python
import glob
import sys
import commands as cmds



def print_progress(percent):
    width = 30

    sys.stdout.write("\t  %.2f%% complete." % percent)
    sys.stdout.write(" |"+"="*int(percent*0.01*width)+" "*int((1.-percent*0.01)*width)+">\r")
    sys.stdout.flush()

tex_files = glob.glob("RA1*.tex")

if len(tex_files) == 0:
	print ">>  Error: no RA1*.tex files found."
	print ">>  Make sure to copy me to the TexFiles directory"
	sys.exit()

# compile all tex files
print "\n>>> Compiling tex files to dvi.\n"
for n, file_name in enumerate(tex_files):
	status = cmds.getstatusoutput("latex %s" % file_name)
	print_progress(100.*float(n)/len(tex_files))
	if status[0] != 0:
		print "Balls up on file: %s" % file_name
		print status


dvi_files = glob.glob("RA1*.dvi")

if len(dvi_files) == 0:
	print ">>  Error: no RA1*.dvi files found."
	print ">>  Check if latex compilation was successful."
	sys.exit()

# convert dvi to pdf
print "\n\n>>> Concerting dvi to pdf.\n"
for n, file_name in enumerate(dvi_files):
	status = cmds.getstatusoutput("dvipdf %s" % file_name)
	print_progress(100.*float(n)/len(dvi_files))
	if status[0] != 0:
		print "Balls up on file: %s" % file_name
		print status

print "\n"