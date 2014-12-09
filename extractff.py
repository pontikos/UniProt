#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/extractff.py,v $
# $Revision: 1.1 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/04/01 13:45:46 $                                                      
# $Author: pontikos $  
#
# $Log: extractff.py,v $
# Revision 1.1  2011/04/01 13:45:46  pontikos
# New python tools.
#
#
#
# *************************************************************
from __future__ import print_function
import argparse
from readchunk import Chunk
from utility_arg_parser import get_input_source

def readindex(indexfilename):
	index={}
	for l in file(indexfilename, 'r').xreadlines():
		start,end,name,releasehash,accs,=l.strip().split(',',4)
		primacc=accs.split(',',1)[0]
		index[primacc]={'start':int(start),'end':int(end),'name':name,'releasehash':releasehash}
	return index

def parse(input, index, infile):
	for l in input.xreadlines():
		acc=l.strip()
		#if not index.get(accs, None): continue
		print(Chunk(infile,index[acc]['start'],index[acc]['end']), end='')


if __name__ == '__main__':
	parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--infile', dest='infile', help="filename to read from.", required=True)
	parser.add_argument('--indexfile', dest='indexfile', help="indexfilename to read from.", required=True)
	#determine input
	input=get_input_source(parser)
	args=parser.parse_args()
	index=readindex(args.indexfile)
	parse(input, index, args.infile)


