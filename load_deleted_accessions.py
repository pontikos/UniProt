#! /sw/arch/bin/python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/load_deleted_accessions.py,v $
# $Revision: 1.4 $                                                                 
# $State: Exp $                                                                     
# $Date: 2011/09/28 12:43:13 $                                                      
# $Author: pontikos $  
#
# $Log: load_deleted_accessions.py,v $
# Revision 1.4  2011/09/28 12:43:13  pontikos
# *** empty log message ***
#
# Revision 1.3  2011/09/27 17:04:47  pontikos
# *** empty log message ***
#
# Revision 1.2  2011/09/26 19:14:12  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/09/22 09:07:03  pontikos
# tool for loading delac_sp.txt into deleted_accessions_sp and delac_tr.txt into deleted_accessions_tr
#
#
#
# *************************************************************
from __future__ import print_function
import sys
import argparse
import re
import subprocess
from multiprocessing import Process
import cx_Oracle
import os
from release_info import read_release

working_release=read_release('working')
working_release_year=working_release.split('_')[0]

# default path to delac_tr
delac_tr_path='/ebi/uniprot/production/tremblnew/trembl_rel_%s/rel%s/Distribution/Ready/delac_tr.txt' % (working_release_year, working_release,)
# there is also a symlink which might points to this file
#/ebi/uniprot/data/trembl_wrel/relnotes/delac_tr.txt
# can also find it on the private ftp
#/ebi/ftp/private/uniprot/knowledgebase/internal/delac_tr.txt

# default path to delac_sp
delac_sp_path='/ebi/sp/misc1/pc/sprot/delac_sp.txt'
# can also find it on the private ftp
#/ebi/ftp/private/uniprot/knowledgebase/docs/delac_sp.txt

parser=argparse.ArgumentParser( formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='' )
mutex_group=parser.add_mutually_exclusive_group(required=True)
mutex_group.add_argument( '--tr', nargs='?', help='load delac_tr.txt into deleted_accessions_tr in swppro', const=delac_tr_path, )
mutex_group.add_argument( '--sp', nargs='?', help='load delac_sp.txt into deleted_accessions_tr in swppro', const=delac_sp_path, )
parser.add_argument('--dbconnection', help='dbconnection details', required=True)
parser.add_argument('--outputdir', help='output dir to send .dat .ctl and .log files', required=True)
args=parser.parse_args()

if args.tr:
    #name of table
    deleted_accessions='DELETED_ACCESSIONS_TR'
    #name of file to load into table
    data=args.tr
elif args.sp:
    #name of table
    deleted_accessions='DELETED_ACCESSIONS_SP'
    data=args.sp
else:
    parser.print_help(file=sys.stderr)
    parser.error('neither --sp nor --tr were specified')


if not os.path.exists(args.outputdir): os.makedirs(args.outputdir)
#os.chdir(args.outputdir)
#print('outputdir:', os.getcwd())
print('outputdir:', args.outputdir)

new_data='%s/%s.dat' % (args.outputdir, deleted_accessions)
print(new_data)
new_data_file=file(new_data,'w')
control='%s/%s.ctl' % (args.outputdir, deleted_accessions)
print(control)

for l in file(data,'r').xreadlines():
    m=re.compile('^(\w{6})$').match(l.strip())
    if not m: continue
    print(m.group(1), file=new_data_file)

new_data_file.flush()
new_data_file.close()
nlines=len(file(new_data,'r').readlines())

print('number of accessions in', data, ':', nlines)

#print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',file=new_data_file)

print("""
OPTIONS (DIRECT=TRUE, ERRORS=1000, SILENT=(FEEDBACK))
LOAD DATA
REPLACE
INTO TABLE {deleted_accessions}
(accession CHAR(15))
""".format(deleted_accessions=deleted_accessions), file=file(control,'w'))

def load():
    cmd="""bsub -I -qproduction -Pprod sqlldr userid={dbconnection} data={data} control={control}""".format(dbconnection=args.dbconnection,data=new_data,control=control)
    print(cmd)
    return_code=subprocess.call(cmd, shell=True)
    return return_code
p=Process(target=load)
p.start()
p.join()

#connect to db and check
c=cx_Oracle.connect(args.dbconnection).cursor()
nrows=len(c.execute('select * from %s'% deleted_accessions).fetchall())

if nrows!=nlines:
    print('Number of lines in', deleted_accessions, 'table in', args.dbconnection, file=sys.stderr)
    print('Number of lines in file', new_data_file, file=sys.stderr)
    raise Exception('Number of rows in db table does not match number of lines in file')

print(nrows, 'rows inserted in', deleted_accessions)

#run checks

