#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/relational.py,v $
# $Revision: 1.1 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/05/27 14:29:18 $                                                      
# $Author: pontikos $  
#
# $Log: relational.py,v $
# Revision 1.1  2011/05/27 14:29:18  pontikos
# make accession list fit in 2 column relational table
#
#
#
# *************************************************************

from __future__ import print_function
import argparse
import sys

parser=argparse.ArgumentParser( formatter_class=argparse.RawDescriptionHelpFormatter )
parser.add_argument('-s', dest='s', type=int, help="where to do the split", required=True)
args=parser.parse_args()

for l in sys.stdin.xreadlines():
	a=l.strip().split(' ')
	a1=a[:args.s]
	a2=a[args.s:]
	if not a2:
		print(*(a1+['']), sep=',')
		continue
	for x in a2:
		print(*(a1+[x]), sep=',')
