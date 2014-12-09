# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/splitff.py,v $
# $Revision: 1.6 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/09/14 16:09:57 $                                                      
# $Author: pontikos $  
#
# $Log: splitff.py,v $
# Revision 1.6  2011/09/14 16:09:57  pontikos
# *** empty log message ***
#
# Revision 1.5  2011/06/21 14:26:05  pontikos
# use Chunk instead of reading a whole section into memory
#
# Revision 1.4  2011/04/01 13:45:46  pontikos
# New python tools.
#
# Revision 1.3  2011/02/25 10:05:18  pontikos
# update to tools
#
#
#
# *************************************************************
from __future__ import print_function
import argparse
import utility_arg_parser
import sys
import os
from mmap import mmap
from readchunk import Chunk

parser=argparse.ArgumentParser()
parser.add_argument('-f', dest='filename', help="name of file to split", required=True)
parser.add_argument('-s', dest='separator', help="separator", required=False, default='//')
group=parser.add_mutually_exclusive_group(required=True)
group.add_argument('-fileno', dest='filenumber', type=int, help="number of subfiles to create")
group.add_argument('-entryno', dest='entrynumber', type=int, help="number of entries per subfile")
parser.add_argument('-p', dest='prefix', help="subfile prefix", default=None)
args=parser.parse_args()

filename_base,filename,= os.path.split(args.filename)
stem,ext,=os.path.splitext(filename)

args.separator='%s\n'%args.separator

if not args.prefix:
	args.prefix=stem

if args.entrynumber:
	filenum=1
	entrynum=0
	outfile=file('%s_%d%s' % (args.prefix,filenum,ext), 'w')
	for l in file(args.filename,'r').xreadlines():
		print(l, file=outfile, end='')
		if l.endswith(args.separator):
			entrynum+=1 
			if entrynum % args.entrynumber == 0:
				outfile.close()
				filenum+=1
				outfile=file('%s_%d%s' % (args.prefix,filenum,ext,), 'w')
else:
	f=open(args.filename, 'r+b')
	m=mmap(f.fileno(), 0)
	s=len(m)
	l=[m.find(args.separator,x)+len(args.separator) for x in [x*s/args.filenumber for x in range(1,args.filenumber)]]
	for ((s,e,), outfile) in zip(map(lambda x,y: (x,y), [0]+l, l+[s]), [file('%s_%d%s'%(args.prefix,filenum,ext),'w') for filenum in range(1,args.filenumber+1)]):
		print(Chunk(args.filename,s,e),file=outfile, end='')
		outfile.close()





