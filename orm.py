#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/orm.py,v $
# $Revision: 1.1 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/04/01 13:45:46 $                                                      
# $Author: pontikos $  
#
# $Log: orm.py,v $
# Revision 1.1  2011/04/01 13:45:46  pontikos
# New python tools.
#
#
#
# *************************************************************

def columnnames_for_tablename(tablename):
	return fetchAllRows("select column_name from all_tab_columns where table_name=:tablename order by column_id", tablename=tablename)

def tablenames_for_columnname(columnname):
	return fetchAllRows("select table_name from all_ind_columns where column_name=:columnname", columnname=columnname)

def DatabaseTable(tablename):
	global db
	class DbTable(object):
		__slots__ = [x for x, in columns_name(tablename)]
		def __init__(self, **keywords):
			object.__init__(self)
			condition=' AND '.join(["%s='%s'"%(k,v,) for k, v, in keywords.items()])
			sql='select * from {tablename} where {condition}'.format(tablename=tablename, condition=condition)
			row=fetchOneRow(sql)
			d=zip(self.__slots__, list(row))
			print sql, row, d
			for a, v, in d: setattr(self, a, v)
		def __repr__(self): return '\n'.join(["%s: %s" % (p, self.__getattribute__(p)) for p in self.__slots__])
		def joined_tables(self, field='%s_ID'%tablename):
			""" All tables which join on a given field default field is name of this table with suffix _ID. """
			return [x for x, in tablenames_for_columnname(field)]
		def all_joined_tables(self):
			""" All tables which join on all given fields of this table. """
			return dict([(s, self.joined_tables(field=s),) for s in self.__slots__])
		def __getattr__(self, name):
			if name in self.__slots__:
				return self.__dict__[name] 
			else:
				columns_names=columnnames_for_tablename(name)
				return [
						DatabaseTable(name)(
							**dict(zip(columns_names, vals)))
						for vals in
						fetchAllRows('select * from {tablename} where {join}'.format(tablename=name,join="%s_ID='%s'"%(tablename,getattr(self,'%s_ID'%tablename,)))) ]
	return DbTable

def fetchOneRow(*a, **k):
	global db
	return db.execute(*a, **k).fetchone() or ()

def fetchAllRows(*a, **k):
	global db
	return db.execute(*a, **k).fetchall() or []


