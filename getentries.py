# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/getentries.py,v $
# $Revision: 1.4 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/04/01 13:45:46 $                                                      
# $Author: pontikos $  
#
# $Log: getentries.py,v $
# Revision 1.4  2011/04/01 13:45:46  pontikos
# New python tools.
#
# Revision 1.3  2011/02/25 10:03:15  pontikos
# renamed readchunkff.py to readchunk.py
#
# Revision 1.2  2011/02/22 18:38:51  pontikos
# python tools to parse FF and distribute jobs on cluster
#
#
# *************************************************************
from __future__ import print_function
import argparse
from utility_arg_parser import get_input_source
import sys
import re


def parse(input, linetype='', searchpatterns=[]):
	#string buffer containing whole entry
	entry_buffer=""
	print_entry=False
	for l in input.xreadlines():
		entry_buffer+=l
		if l.startswith(linetype) and any([regex.search(l) for regex in searchpatterns]): print_entry=True
		#end of ff entry
		if l.startswith('//'):
			if print_entry: print( entry_buffer, end="" )
			entry_buffer=""
			print_entry=False


if __name__ == '__main__':
	parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--linetype', dest='linetype', default='', required=False)
	group=parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--searchpatterns', nargs="*", action='store', dest='searchpatterns', help="searchpatterns separated by spaces")
	group.add_argument('--searchpatternsfile',dest='searchpatternsfile')
	#determine input
	input=get_input_source(parser)
	args=parser.parse_args()
	if args.searchpatterns:
		searchpatterns=[re.compile(s) for s in args.searchpatterns]
	elif args.searchpatternsfile:
		searchpatterns=[re.compile(l.strip()) for l in file(args.searchpatternsfile,'r').xreadlines()]
	else:
		raise Exception('No searchpatterns specified')
	parse(input, linetype=args.linetype, searchpatterns=searchpatterns)


