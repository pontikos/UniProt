# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/indexff.py,v $
# $Revision: 1.2 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/02/28 12:47:30 $                                                      
# $Author: pontikos $  
#
# $Log: indexff.py,v $
# Revision 1.2  2011/02/28 12:47:30  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/02/25 10:03:15  pontikos
# renamed readchunkff.py to readchunk.py
#
# Revision 1.2  2011/02/22 18:38:51  pontikos
# python tools to parse FF and distribute jobs on cluster
#
#
# *************************************************************
import md5
import re
import utility_arg_parser
import argparse

def parse(input):
	#string buffer containing whole entry
	entry_buffer=""
	id=''
	acs=[]
	last_byte=first_byte=-1
	#n is the absolute byte position
	n=input.start
	for l in input.xreadlines():
		entry_buffer+=l
		if l.startswith('ID'):
			m = re.compile('^ID   (.*?) ').match(l)
			id=m.group(1)
			first_byte=n
		if l.startswith('AC'):
			m = re.compile('^AC   (.*?)$').match(l)
			acs+=[a.strip() for a in m.group(1).split(';') if a]
		n+=len(l)
		#end of ff entry
		if l.startswith('//'):
			last_byte=n
			#compute hash of entry to see if it's changed since indexing
			entry_checksum = md5.md5(entry_buffer).hexdigest()
			print "%d,%d,%s,%s,%s" % (first_byte, last_byte, id, entry_checksum, ','.join(acs))
			#reset values
			entry_buffer=""
			id=''
			acs=[]
			last_byte=first_byte=-1

if __name__ == '__main__':
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	#determine input
	input=utility_arg_parser.get_input_source(parser)
	args=parser.parse_args()
	#print input.start
	parse(input)


