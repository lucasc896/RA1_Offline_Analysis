#!/usr/bin/env python
import os
import glob
import sys
import commands as cmds

def print_progress(percent):
    width = 30

    sys.stdout.write("\t  %.2f%% complete." % percent)
    sys.stdout.write(" |"+"="*int(percent*0.01*width)+" "*int((1.-percent*0.01)*width)+">\r")
    sys.stdout.flush()

class Chdir:         
  def __init__( self, newPath ):  
    self.savedPath = os.getcwd()
    os.chdir(newPath)

  def __del__( self ):
    os.chdir( self.savedPath )

def check_headers(files = None):

	if any("ptdr-definitions.tex" in p for p in files):
		if any("symbols.tex" in s for s in files):
			return True

	return False

def process_files(directory = None):

	# copy in tex headers
	# first find where they are
	header_files = glob.glob("*.tex")

	if not check_headers(header_files):
		header_files = glob.glob("../*.tex")
		if not check_headers(header_files):
			print ">>  Error: could not locate latex header files."
			sys.exit()

	for header in header_files:
		cmds.getstatusoutput("cp %s %s" % (header, directory))

	change_op = Chdir(directory)

	tex_files = glob.glob("RA1*.tex")

	if len(tex_files) == 0:
		print ">>  Error: no RA1*.tex files found."
		print ">>  Check files are present in given directory."
		sys.exit()

	# compile all tex files
	print "\n>>> Compiling tex files to dvi.\n"
	for n, file_name in enumerate(tex_files):
		status = cmds.getstatusoutput("latex %s" % file_name)
		print_progress(100.*float(n)/len(tex_files))
		if status[0] != 0:
			print "Balls up on file: %s" % file_name
			print status
	print_progress(100.)

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
	print_progress(100.)

	print "\n\n>>> Cleaning up all files ['gz', 'aux', 'dvi', 'log']\n"
	status = cmds.getstatusoutput("rm *gz *aux *dvi *log")

if __name__ == '__main__':

	if len(sys.argv) < 2:
		print ">>  Error: Please pass a tex file directory."
		print ">>  e.g. ./make_latex_files.py <directory>"
		sys.exit()

	process_files(directory = sys.argv[1])