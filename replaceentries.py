#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: $
# $Revision: $                                                                 
# $State: $                                                                     
# $Date: $                                                      
# $Author: $  
#
# $Log: $
#
#
# *************************************************************
from __future__ import print_function
import argparse
import sys
from crc64 import *
import md5
import re
import utility_arg_parser
from collections import defaultdict

def update(format, input, updatefile):
	pass


def fasta_remove(input, accessions):
	for l in input.xreadlines():
		if l.startswith('>'):
			acc=l.split('|')[1]
			if acc in accessions:
				output=sys.stderr
			else:
				output=sys.stdout
		print(l,file=output,end='')

def text_remove(input, accessions):
	for l in input.xreadlines():
		if l.startswith('ID   '):
			buffer=l
			acc=None
			continue
		if not acc and l.startswith('AC   '):
			acc=l.split('   ')[1].split(';')[0].rstrip().strip()
			if acc in accessions:
				output=sys.stderr
			else:
				output=sys.stdout
		print(buffer,l,file=output,sep='', end='')
		buffer=''


REMOVE={'fasta':fasta_remove, 'text':text_remove}

if __name__ == '__main__':
	#usage = "Usage: %prog <options>"
	#parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	group=parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--update', dest='updatefile', help="File containing entries to replace.")
	group.add_argument('--remove', dest='removefile', help="""File containing accessions of entries to remove.
	In this mode removed entries printed to stderr while entries which are kept are printed to stdout.""")
	parser.add_argument('--format', dest='format', choices=['text', 'xml', 'fasta'], default='text', help="Format of input file.")
	#determine input
	input=utility_arg_parser.get_input_source(parser)
	args=parser.parse_args()
	if args.updatefile:
		update(format=args.format, input=input, updatefile=file(args.updatefile,'r'))
	else:
		accessions=frozenset([acc.strip() for acc in file(args.removefile,'r')])
		REMOVE[args.format](input=input, accessions=accessions)


