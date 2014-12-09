#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/parse_sql_checks.py,v $
# $Revision: 1.7 $
# $State: Exp $
# $Date: 2011/09/26 19:14:28 $
# $Author: pontikos $
#
# $Log: parse_sql_checks.py,v $
# Revision 1.7  2011/09/26 19:14:28  pontikos
# *** empty log message ***
#
# Revision 1.6  2011/09/20 13:35:57  pontikos
# *** empty log message ***
#
# Revision 1.5  2011/08/26 14:12:35  pontikos
# *** empty log message ***
#
# Revision 1.4  2011/08/26 12:46:30  awilter
# fixed 'max' option
#
# Revision 1.3  2011/08/26 09:21:30  pontikos
# *** empty log message ***
#
# Revision 1.2  2011/07/08 16:08:08  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/07/08 12:57:09  pontikos
# parses the sql files to extract queries. Each query has a key, description and sql
#
#
#
# *************************************************************
from __future__ import print_function
import sys
import cx_Oracle
import re
import argparse
import utility_arg_parser
import os
from multiprocessing import Process
#shell
import subprocess
from time import ctime

class Query(object):
    def __init__(self):
        self.key = ''
        self.description = ''
        self.sql = []
        self.rows = None
        self.description = None
    def __repr__(self):
        return '<KEY:%s,DESCRIPTION:%s>' % (self.key, self.description)
    def query(self, dbconnection):
        #w=Process(target=bsub, kwargs={'jobname':'%s_%d'%(args.map_jobname,i), 'cmd':'%s %s %s > %s'%(readchunk,args.map,file_slice,slice_filename,),'blocking':True})
        #workers.append(w)
        #w.start()
        #w.join
        self.query_start_time = ctime()
        dbcursor = cx_Oracle.connect(dbconnection).cursor()
        dbcursor.setoutputsize(10)
        self.rows = dbcursor.execute(self.sql).fetchall()
        self.column_names = [x[0] for x in dbcursor.description]
        dbcursor.close()
        self.query_end_time = ctime()
    def xml(self):
        return """
        <query key='{key}'>
            <description>
                {description}
            </description>
            <sql> {sql} </sql>
        </query> """.format(key = self.key, description = self.description, sql = self.sql)
    def html(self, max):
        print ("""
        <h4>
        KEY:
        <a href="http://www.ebi.ac.uk/panda/jira/browse/{key}"> {key} <a>
        </h4>
        <h4>
        DESCRIPTION:
        </h4>
        {description}
        <h4>
        SQL:
        </h4>
        <code class="prettyprint lang-sql"> {sql} </code>
        """.format(key = self.key, description = self.description, sql = self.sql))
        if self.rows is None: return
        nrows = len(self.rows)
        if len(self.rows) > 0:
            color = 'red'
        else:
            color = 'green'
        print('<h4>QUERY START TIME:</h4>', self.query_start_time)
        print('<h4>QUERY END TIME:</h4>', self.query_end_time)
        print('<h4> <font color="{color}"> RESULTS: {nrows} rows </font> </h4>'.format(color = color, nrows = nrows))
        if nrows == 0: return
        print("""<table id="{key}" border="1">""".format(key = self.key))
        print('<tr>')
        for column_name in self.column_names:
            print('<th>', column_name, '</th>')
        print('</tr>')
        for r in self.rows[:max]:
            print('<tr>')
            for x in r:
                print('<td>', x, '</td>')
            print('</tr>')
        print('</table>')


#extract queries from sql file and return dict containing query objects
def parse_sql(input):
    queries = {}
    #for l in [x for x in file(check_file,'r').read().split(';') if x.strip()]:
    for l in [x for x in input.read().split(';') if x.strip()]:
        q = Query()
        metadata = re.compile('PROMPT "(.*?)"').findall(l)
        for m in metadata:
            if not q.key: q.key = m.replace(' ', '_').replace('/', '-')
            q.description = m
            if not ':' in m:
                continue
            key, value, = m.split(':')
            key = key.strip()
            value = value.strip()
            if key == 'KEY': q.key = value
        if not q.description: continue
        for y in l.split('\n'):
            #certain lines are ignored
            y = y.strip()
            if not y: continue
            if y.startswith('--'): continue
            if y.startswith('@'): continue
            if y == '!date': continue
            if re.compile('^PROMPT "(.*?)"').search(y.strip()): continue
            q.sql.append(y)
        if not q.sql: continue
        q.sql = ' '.join(q.sql)
        queries[q.key] = q
    return queries

if __name__ == '__main__':
    usage_example = ''
    parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, epilog = usage_example)
    parser.add_argument('--list', dest = 'list', choices = ['keys'])
    parser.add_argument('--key', dest = 'key', action = 'append')
    parser.add_argument('--format', dest = 'format', choices = ['xml', 'html'], help = "format sql", default = 'xml')
    parser.add_argument('--dbconnection', dest = 'dbconnection', help = "username/password@dbname", required = False)
    parser.add_argument('--max', dest = 'max', help = "maximum number of rows to display in output", type = int, default = 1000, required = False)
    #parser.add_argument('--email', dest='email', help="", required=False)
    #group=parser.add_mutually_exclusive_group(required=True)
    #parser.add_argument('--check-name', dest='check_name', choices=['valid', 'pre-redundancy', 'post-redundancy', 'deleted_accessions'],  help="")
    #parser.add_argument('--key', dest='key', help="JIRA key of the sql query to run", required=False)
    #parser.add_argument('--out', dest='outformat', choices=['html', 'csv'], help="format of output", default='html')
    #determine input
    input = utility_arg_parser.get_input_source(parser)
    args = parser.parse_args()
    queries = parse_sql(input)
    #only get queries requested by key
    if args.key:
        queries = dict([(k, queries[k],) for k in args.key])
    if args.list == 'keys':
        for k in queries:
            print(queries[k].key)
    elif args.format == 'xml':
        print ('<?xml version="1.0" encoding="UTF-8"?>')
        print('<queries>')
        for k in queries:
            print(queries[k].xml())
        print('</queries>')
    elif args.format == 'html':
        print("""
        <html>
        <head>
        <link href="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.css" type="text/css" rel="stylesheet" />
        <script type="text/javascript" src="http://google-code-prettify.googlecode.com/svn/trunk/src/prettify.js"></script>
        <script type="text/javascript" src="http://google-code-prettify.googlecode.com/svn/trunk/src/lang-sql.js"></script>
        """)
        print("""
        <title> {keys} </title>
        </head>
        <body onload="prettyPrint()" >
        """.format(keys = ','.join([k for k in queries])))
        for k in queries:
            if args.dbconnection:
                queries[k].query(args.dbconnection)
            queries[k].html(args.max)
            print('<hr></hr>')
        print("""
        </body>
        </html>
        """)



