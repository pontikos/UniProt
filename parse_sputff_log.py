#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/parse_sputff_log.py,v $
# $Revision: 1.3 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/08/02 14:05:55 $                                                      
# $Author: pontikos $  
#
# $Log: parse_sputff_log.py,v $
# Revision 1.3  2011/08/02 14:05:55  pontikos
# bug in parser
#
# Revision 1.2  2011/06/30 18:32:39  pontikos
# handle more sputff errors
#
# Revision 1.1  2011/06/29 16:28:45  pontikos
# quick script for parsing output of java sputff
#
#
#
# *************************************************************
from __future__ import print_function
from collections import defaultdict
from BeautifulSoup import BeautifulSoup
import sys

ERROR=defaultdict(list)
bs=BeautifulSoup(sys.stdin)
ERROR_ACC=set()
for e in bs.findAll('error'):
	ERROR_ACC.add(e.entry.text)
	if 'IllegalStateException' in e.message['name']:
		ERROR[e.message.text].append(e.entry.text)
		continue
	if 'Cv_journal does not have type:' in e.message.text and 'IllegalTypeException' in e.message['name']:
		ERROR[e.message.text].append(e.entry.text)
		continue
	if 'Internal Exception: java.sql.BatchUpdateException: ORA-01403: no data found' in e.message.text and 'TremblException' in e.message['name']:
		ERROR['ORA-01403: no data found'].append(e.entry.text)
		continue
	if 'Internal Exception: java.sql.BatchUpdateException: ORA-00001: unique constraint' in e.message.text and 'TremblException' in e.message['name']:
		ERROR['ORA-00001: unique constraint'].append(e.entry.text)
		continue
	if 'Internal Exception: java.sql.BatchUpdateException: ORA-12899: value too large for column' in e.message.text and 'TremblException' in e.message['name']:
		ERROR['ORA-12899: value too large for column'].append(e.entry.text)
		continue
	ERROR['UNKNOWN'].append(e.entry.text)

for error_type in ERROR:
	print('***', error_type)
	for e in ERROR[error_type]:
		print(e)

for acc in ERROR_ACC:
	print(acc, file=sys.stderr)


