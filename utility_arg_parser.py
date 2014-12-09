# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/utility_arg_parser.py,v $
# $Revision: 1.5 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/07/08 15:14:33 $                                                      
# $Author: pontikos $  
#
# $Log: utility_arg_parser.py,v $
# Revision 1.5  2011/07/08 15:14:33  pontikos
# add read to I
#
# Revision 1.4  2011/03/31 14:17:39  pontikos
# *** empty log message ***
#
# Revision 1.3  2011/02/28 12:47:30  pontikos
# *** empty log message ***
#
# Revision 1.2  2011/02/25 10:02:20  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/02/22 18:38:51  pontikos
# python tools to parse FF and distribute jobs on cluster
#
#
# *************************************************************
import sys
from mmap import mmap
import argparse
from readchunk import Chunk

def get_input_source(parser):
	""" Determine where input comes from. """
	group=parser.add_mutually_exclusive_group(required=False)
	group.add_argument('--file_slice', dest='file_slice', help="FILE_SLICE format infile:start-end. Where start and end are byte indexes.", default=None)
	group.add_argument('--file', dest='file', help="FILE to read from.", default=None)
	args = parser.parse_args()

	if args.file_slice:
		infile,section,=args.file_slice.split(':')
		start,end,=[int(x) for x in section.split('-')]
		input=Chunk(infile, start, end)
	elif args.file:
		#extend the file type to include start and end fields
		input=type('I',(file,),{'start':-1,'end':-1})(args.file, 'r')
		input.start=0
	else:
		class I(object):
			start=0
			end=-1
			def xreadlines(self): return sys.stdin.xreadlines()
			def read(self): return sys.stdin.read()
		input=I()
	return input

