#!/usr/bin/env python

'''
To check the tabel TREMBL_DELETIONS against SWPREAD and report the relative modification (in %) per Tax_ID
The percentage number must be small otherwise there's something wrong likely in ENA
'''

# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/checkDeletions.py,v $
#
# $Log: checkDeletions.py,v $
# Revision 1.1  2011/09/21 10:31:54  awilter
# - new checkDeletetions.py
# - tidied functions.sh and sptr.make
#

import argparse
from cx_Oracle import connect

# YOU ARE ALLOWED TO CHANGE THOSE VARIABLES IF YOU KNOW WHAT YOU'RE DOING
dbServer = 'SPTR_READONLY/readonly_sptr@swppro'
#dbServerPR = 'prot_select/selectonly@prpro'

sqlDel = """
select e.tax_id, count(*) as N
from TREMBL_DELETION d, EMBL_PROTEIN_ID p, dbentry e
where d.accession=p.protein_id and p.dbentry_id=e.dbentry_id group by e.tax_id having count(e.accession) > %(cutoff)s order by e.tax_id
"""

sqlRef = """
select d.tax_id, count(distinct d.accession) as N from dbentry@swpread d where d.tax_id in
(select e.tax_id
from TREMBL_DELETION d, EMBL_PROTEIN_ID p, dbentry e
where d.accession=p.protein_id and p.dbentry_id=e.dbentry_id group by e.tax_id having count(e.accession) > %(cutoff)s)
and d.deleted='N'
and d.merge_status <> 'R'
and d.entry_type in (0,1)
group by d.tax_id order by d.tax_id
"""

sqlTaxo = """
select t.tax_id, t.sptr_code, t.ncbi_scientific from TAXONOMY.tax_node t where t.tax_id in (%(taxDel)s)
"""

sqlKWread = """
select p2u.tax_id, count(*) from sptr.proteome2uniprot@swpread p2u where p2u.tax_id in (%(taxDel)s)
group by p2u.tax_id order by p2u.tax_id
"""

sqlKWpro = """
select p2u.tax_id, count(*) from proteome2uniprot p2u where p2u.tax_id in (%(taxDel)s)
group by p2u.tax_id order by p2u.tax_id
"""

#########################################################################

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cutoff', dest = 'cutoff', help = "set the threshold for reporting modifications (absolute changes)", default = 10, type = int)
    args = parser.parse_args()

    cursor = connect(dbServer).cursor()

    cursor.execute(sqlRef % {'cutoff':args.cutoff})
    dictRef = dict(cursor.fetchall())

    cursor.execute(sqlDel % {'cutoff':args.cutoff})
    dictDel = dict(cursor.fetchall())

    cursor.execute(sqlTaxo % {'taxDel': ",".join(map(str, dictDel.keys()))})
    table = cursor.fetchall()

    cursor.execute(sqlKWread % {'taxDel': ",".join(map(str, dictDel.keys()))})
    dictKWread = dict(cursor.fetchall())

    cursor.execute(sqlKWpro % {'taxDel': ",".join(map(str, dictDel.keys()))})
    dictKWpro = dict(cursor.fetchall())

    report = "Report: Species with number of changes > %s after EMBL-IMPORT (SWPREAD x SWPPRO)\n" % args.cutoff
    report += "Tax_ID   OSCODE   KW    Difference                NCBI_SciName\n"

    for taxId, oscode, ncbiSciName in table:
        if oscode:
            nRef = dictRef.get(taxId, 0)
            nDel = dictDel.get(taxId, 0)
            relDiff = nDel * 100.0 / nRef
            msg = "%3.2f%% (%i of %i)" % (relDiff, nDel, nRef)
            cKWr = dictKWread.get(taxId)
            cKWp = dictKWpro.get(taxId)
            kwr = 'N'
            kwp = 'N'
            if cKWr:
                kwr = 'Y'
            if cKWp:
                kwp = 'Y'
            report += '%-8s %-8s %s|%s : %-25s "%s"\n' % (taxId, oscode, kwr, kwp, msg, ncbiSciName)
    print(report)
