#! /usr/bin/env python
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/entry2csv.py,v $
# $Revision: 1.3 $
# $Date: 2011/05/09 12:17:59 $
# $Author: pontikos $
# $Log: entry2csv.py,v $
# Revision 1.3  2011/05/09 12:17:59  pontikos
# embl pids
#
# Revision 1.2  2011/03/31 13:37:41  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/02/22 18:38:51  pontikos
# python tools to parse FF and distribute jobs on cluster
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

## {{{ http://code.activestate.com/recipes/576720/ (r6)
#essentially this allows functions to be called like variables
#useful when we want to do some pre-processing on a variable before returning it
def lazyproperty(func):
	"""A decorator for lazy evaluation of properties """
	cache = {}
	def _get(self):
		try:
			return cache[self]
		except KeyError:
			cache[self] = value = func(self)
			return value
	return property(_get)
## end of http://code.activestate.com/recipes/576720/ }}}

class UniprotEntry(object):
	__slots__ = [
				'__accessions__',
				#first dt line
				'entry_type',
				'first_public',
				#second dt line
				'sequence_date',
				'sequence_version',
				#sequence buffer containing sequence
				'sequence_buffer',
				'sequence_crc',
				'sequence_length',
				#third dt line
				'entry_date',
				'entry_version',
				#string buffer containing whole entry except dt lines
				'entry_buffer',
				#whole entry buffer
				'whole_entry_buffer',
				'__xrefs__'
				]
	def __init__(self):
		self.__accessions__=[]
		self.sequence_buffer=''
		self.entry_buffer=''
		self.whole_entry_buffer=''
		self.__xrefs__=defaultdict(list)
	@lazyproperty
	def sequence_checksum(self): return md5.md5(self.sequence_buffer.replace(' ','').replace('\n','').strip()).hexdigest()
	@lazyproperty
	def entry_checksum(self): return md5.md5(self.entry_buffer).hexdigest()
	@lazyproperty
	def all_acc(self): return ';'.join(self.__accessions__)
	@lazyproperty
	def primary_acc(self): return self.__accessions__[0]
	@lazyproperty
	def secondary_acc(self): return self.__accessions__[1:]
	@lazyproperty
	def whole_entry_checksum(self): return md5.md5(self.whole_entry_buffer).hexdigest()
	@lazyproperty
	def embl_crossref(self): return ','.join(set(self.__xrefs__['EMBL']))
	def __str__(self):
		return ','.join([getattr(self,f) for f in print_fields])

def parse(input, endline):
	entry=UniprotEntry()
	for l in input.xreadlines():
		#ignore copyright
		if l.startswith('CC   ---'): continue
		if l.startswith('CC   Copyrighted by the UniProt Consortium, see http://www.uniprot.org/terms'): continue
		if l.startswith('CC   Distributed under the Creative Commons Attribution-NoDerivs License'): continue
		if l.startswith('**'): continue
		#sys.stdout.write( l )
		m = re.compile('^AC   (.*?)$').match(l)
		if m:
			entry.__accessions__ += [x.strip() for x in m.group(1).split(';') if x.strip()]
		#entry.whole_entry_buffer += l
		#none of the 3 dt lines are included in entry buffer
		m = re.compile('^DT   (.*?), integrated into UniProtKB/(TrEMBL|Swiss-Prot).$').match(l)
		if m:
			entry.first_public = m.group(1)
			entry.entry_type = m.group(2)
			continue
		m = re.compile('^DT   (.*?), sequence version (\d+).$').match(l)
		if m:
			entry.sequence_date = m.group(1)
			entry.sequence_version = m.group(2)
			continue
		m = re.compile('^DT   (.*?), entry version (\d+).$').match(l)
		if m:
			entry.entry_date = m.group(1)
			entry.entry_version = m.group(2)
			continue
		m=re.compile('DR   ([^;]+); ([^;]+); ([^;]+); ([^;]+)').search(l)
		if m: entry.__xrefs__[m.group(1)].append(m.group(3))
		m = re.compile('^SQ   SEQUENCE   (\d+) AA;  (\d+) MW;  (\w{16}) CRC64;').match(l)
		if m:
			entry.sequence_length = int(m.group(1))
			entry.sequence_crc = m.group(3)
		#in the ff sequences start with 2 spaces
		if l.startswith('  '): entry.sequence_buffer += l
		#entry_buffer contains whole entry except DT lines, CC Copyright lines, internal annotation
		#lines which start with ** and AC lines
		entry.entry_buffer += l
		#end of ff entry
		if l.startswith('//'):
			entry.sequence_buffer=entry.sequence_buffer.replace(' ','').replace('\n','').strip()
			#sanity check
			if entry.sequence_crc != CRC64digest(entry.sequence_buffer) or entry.sequence_length != len(entry.sequence_buffer):
				print(entry.sequence_crc, CRC64digest(entry.sequence_buffer), sep=" ", file=sys.stderr)
				print(entry.sequence_length, len(entry.sequence_buffer), sep=" ", file=sys.stderr)
				raise Exception("Mismatch between computed and sequence CRC64 or length in file!")
			print(entry,end=endline)
			#new entry
			del entry
			entry=UniprotEntry()
			continue


if __name__ == '__main__':
	#usage = "Usage: %prog <options>"
	#parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser = argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	default_print_fields=['primary_acc', 'first_public', 'entry_type', 'sequence_date', 'sequence_version', 'sequence_checksum', 'entry_date', 'entry_version', 'entry_checksum']
	print_field_options=[x for x in dir(UniprotEntry) if not x.startswith('__')]
	parser.add_argument('-e', dest='endline', default='\n')
	parser.add_argument('-p', dest='print_fields', action='store', nargs="*",
			help="Fields of entry to print in csv format.", choices=print_field_options, default=default_print_fields)
	#determine input
	input=utility_arg_parser.get_input_source(parser)
	args=parser.parse_args()
	global print_fields
	print_fields=args.print_fields
	parse(input, args.endline)


