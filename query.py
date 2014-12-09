#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: $
# $Revision: $                                                                 
# $State: $                                                                     
# $Date: $                                                      
# $Author: $  
#
# $Log: $
#
#
# *************************************************************
import sys
import cx_Oracle
import re
import argparse
import utility_arg_parser
import os
from multiprocessing import Process

class Query(object):
	def __init__(self):
		self.key=None
		self.description=None
		self.sql=""
		self.rows=None
		self.description=None
	def __repr__(self):
		return '<KEY:%s,DESCRIPTION:%s>' % (self.key, self.description)
	def query(self, dbconnection):
		dbcursor=cx_Oracle.connect(dbconnection).cursor()
		self.rows=dbcursor.execute(self.sql).fetchall()
		self.column_names=[x[0] for x in dbcursor.description]
		dbcursor.close()
		print self.rows[0]


if __name__ == '__main__':
	q=Query()
	q.key='K1'
	q.description='BLAH'
	q.sql="select * from dbentry where rownum < 100"
	#q.query('sptr/sptruser@swpdev')
	#w=Process(target=q.query, kwargs={'jobname':'%s_%d'%(args.map_jobname,i), 'cmd':'%s %s %s > %s'%(readchunk,args.map,file_slice,slice_filename,),'blocking':True})
	#workers.append(w)
	w=Process(target=q.query, args=('sptr/sptruser@swpdev',))
	w.start()
	print 'hello'
	#w.join

