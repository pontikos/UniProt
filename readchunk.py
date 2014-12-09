# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/readchunk.py,v $
# $Revision: 1.4 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/09/14 16:09:57 $                                                      
# $Author: pontikos $  
#
# $Log: readchunk.py,v $
# Revision 1.4  2011/09/14 16:09:57  pontikos
# *** empty log message ***
#
# Revision 1.3  2011/03/31 14:11:19  pontikos
# *** empty log message ***
#
# Revision 1.2  2011/02/28 12:47:30  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/02/25 10:02:20  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/02/22 18:38:51  pontikos
# python tools to parse FF and distribute jobs on cluster
#
#
# *************************************************************
from __future__ import print_function
from mmap import mmap
import argparse
import sys

class Chunk(object):
	def __init__(self, infile, start, end):
		f=open(infile, 'r+b')
		self.m=mmap(f.fileno(), 0)
		self.m.seek(start)
		self.start=int(start)
		self.end=int(end)
	def read(self):
		return self.m.read(end-start)
	def xreadlines(self):
		while self.m.tell() < self.end:
			yield self.m.readline()
	def __repr__(self):
		return ''.join([l for l in self.xreadlines()])


if __name__ == '__main__':
	parser=argparse.ArgumentParser()
	#params: infile command #slices outfile
	parser.add_argument('-f', dest='infile', help="file to read from.", required=True)
	parser.add_argument('-s', dest='start', type=int, help="starting byte position", required=True)
	parser.add_argument('-e', dest='end', type=int, help="end byte position",  required=True)
	args=parser.parse_args()
	chunk=Chunk(args.infile, args.start, args.end)
	print(chunk, end='')


