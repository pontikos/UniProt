#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/uniprot_orm.py,v $
# $Revision: 1.1 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/04/01 13:45:46 $                                                      
# $Author: pontikos $  
#
# $Log: uniprot_orm.py,v $
# Revision 1.1  2011/04/01 13:45:46  pontikos
# New python tools.
#
#
#
# *************************************************************
import orm

def UniprotEntryComponent(uniprot_entry, tablename):
	class UniprotEntryComponent(orm.DatabaseTable(tablename)):
		def __init__(self, *args):
			for a, v, in zip(self.__slots__, args):
				setattr(self, a, v)
		def __getattr__(self, name):
			if name in self.__slots__:
				return self.__dict__[name] 
			else:
				return UniprotEntryComponent(self, name)
	return [ UniprotEntryComponent(*vals) for vals in list(orm.fetchAllRows('select * from %s where dbentry_id=:dbentry_id' % tablename, dbentry_id=uniprot_entry.DBENTRY_ID)) ]

class UniprotEntry(orm.DatabaseTable('DBENTRY')):
	def __init__(self, accession=None):
		#super(DatabaseTable, self).__init__()
		#needed for __slots__ to be accessible
		##object.__init__(self)
		for a, v, in zip(self.__slots__, list(orm.fetchOneRow('select * from dbentry where accession=:accession', accession=accession))):
			setattr(self, a, v)
	def __getattr__(self, name):
		if name in self.__slots__:
			return self.__dict__[name] 
		else:
			return UniprotEntryComponent(self, name)
