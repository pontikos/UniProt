#! /usr/bin/env python
#
# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/release_info.py,v $
# $Revision: 1.9 $
# $State: Exp $
# $Date: 2011/09/28 12:13:10 $
# $Author: awilter $
#
# $Log: release_info.py,v $
# Revision 1.9  2011/09/28 12:13:10  awilter
# sendEmail()
#
# Revision 1.8  2011/09/28 12:04:17  awilter
# sendEmail()
#
# Revision 1.7  2011/09/28 07:17:13  pontikos
# *** empty log message ***
#
# Revision 1.6  2011/09/09 08:26:07  awilter
# improved performance and robustness
#
# Revision 1.5  2011/09/08 14:58:44  awilter
# several improvements, using 'history' file to track releases and shifts
#
# Revision 1.3  2011/08/23 14:22:30  pontikos
# *** empty log message ***
#
# Revision 1.2  2011/08/18 10:00:11  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/08/17 20:30:37  pontikos
# simpler better approach to up_rel which hopefully will replace this script
#
#
#
# *************************************************************
from __future__ import print_function
from email.mime.text import MIMEText
import argparse
import datetime
import sys
import smtplib

#files:
#/ebi/uniprot/data/release_info/working
#/ebi/uniprot/data/release_info/working_release_date
#/ebi/uniprot/data/release_info/private
#/ebi/uniprot/data/release_info/private_release_date
#/ebi/uniprot/data/release_info/public
#/ebi/uniprot/data/release_info/public_release_date

# all releases with its dates goes there and there you enter the future releases
# for which dates will shift
#/ebi/uniprot/data/release_info/history


path = '/ebi/uniprot/data/release_info/'
#path = '/homes/pontikos/release_info/' #debug
#path = '/Users/alan/Downloads/release/' # debug

fromEmail = 'uniprot-prod@ebi.ac.uk'
toEmail = 'trembldev@ebi.ac.uk'
DATE_FMT_DEFAULT = '%d-%b-%Y'
DATE_FMT = DATE_FMT_DEFAULT
DELTA = 28

def sendEmail(key, release_number):
    txt = 'working release: %s %s\n' % (read_release('working'), read_release_date('working'))
    txt += 'private release: %s %s\n' % (read_release('private'), read_release_date('private'))
    txt += 'public  release: %s %s\n' % (read_release('public'), read_release_date('public'))
    txt += """
Don't forget to relogin or "source $CVS_RO/src/sh/sp_wr/variables.sh" to update your %s env variable
""" % (key)
    msg = MIMEText(txt)
    msg['Subject'] = '%s updated to %s' % (key, release_number)
    msg['From'] = fromEmail
    msg['To'] = toEmail
    s = smtplib.SMTP('localhost')
    s.sendmail(fromEmail, [toEmail], msg.as_string())
    s.quit()

## reads from /ebi/uniprot/data/release_info/
def read_release(info):
    return file(path + info, 'r').read().strip()

#this must always be true
# working >= private >= public
def check(working = read_release('working'), private = read_release('private'), public = read_release('public')):
    if working >= private >= public:
        return True
    else:
        print('%s >= %s >= %s' % (working, private, public,))
        raise Exception('condition working >= private >= public violated')

def read_release_date(info):
    return datetime.datetime.strptime(file(path + '%s_release_date' % info, 'r').read().strip(), DATE_FMT_DEFAULT).strftime(DATE_FMT)

def write_release(info, release): file(path + info, 'w').write(release)

def write_release_date(info, release_date):
    file(path + '%s_release_date' % info, 'w').write(release_date)

def increment_release(release):
    """
    If next release date in in the new year, then release number needs its year
    to be reset
    """
    release_date = when(release)
    next_release_date = increment_release_date(release_date, DELTA)
    #year = int(release_date.split('-')[-1])
    next_year = int(next_release_date.split('-')[-1])
    year, number, = map(int, release.split('_'))
    if next_year != year:
        year += 1
        number = 1
    else:
        number += 1
    return '%4d_%02d' % (year, number,)

def decrement_release(release):
    """
    If previous release is in the previous year, then release number needs its year
    to
    """
    return

def increment_release_date(release_date, DELTA):
    next_release_date = datetime.timedelta(days = DELTA) + datetime.datetime.strptime(release_date, DATE_FMT)
    return next_release_date.strftime(DATE_FMT)

def check_against_public(next_working):
    """
        public_release cannot be more than 2 numbers different from working_release
        if it happens, someone, somewhere forgot to updates private and public accordingly
    """
    public = file(path + 'public', 'r').read().strip()
    yp, mp = map(int, public.split('_'))
    yw, mw = map(int, next_working.split('_'))
    diff = ((yw * 12 + mw) - (yp * 12 + mp))
    if diff > 2:
        print("Sorry, cannot update 'working release' to %s since 'public release' is still %s" % (next_working, public), file = sys.stderr)
        sys.exit(1)

def loadHistory():
    # load data from history (it also contains eventual shifts)
    historyDict = {}
    for item in file(path + 'history', 'r').readlines():
        try:
            relNum, relDate = item.split()
            historyDict[relNum] = relDate
        except:
            pass
    return historyDict

def saveHistory(release, release_date):
    historyDict = loadHistory()
    historyDict[release] = release_date
    # sort historyDict and save in history file
    releases = historyDict.keys()
    releases.sort()
    txtHist = "\n".join(["%s %s" % (x, historyDict.get(x)) for x in releases ])
    file(path + 'history', 'w').write(txtHist)

def when(release):
    historyDict = loadHistory()
    when_date = historyDict.get(release)
    if when_date: return when_date
    tmpRel = historyDict.keys()
    tmpRel.append(release)
    tmpRel.sort()
    id = tmpRel.index(release)
    if id == 0:
        print("Sorry, cannot compute date for release '%s'" % args.when, file = sys.stderr)
        return
    refRel = tmpRel[id - 1] # refRel (reference release number) is the previous closest one to args.when
    year, number, = map(int, release.split('_'))
    ref_year, ref_number, = map(int, refRel.split('_'))
    when_date = (datetime.timedelta(days = 12 * DELTA * (year - ref_year) + DELTA * (number - ref_number)) + datetime.datetime.strptime(historyDict.get(refRel), DATE_FMT)).strftime(DATE_FMT)
    when_year = int(when_date.split('-')[-1])
    if when_year != year:
        print("Sorry, this release number is not possible!", file = sys.stderr)
        return
    else:
        return when_date

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter, description = 'Reads and updates the release number and release date found in %s' % path)
    #read_group=parser.add_argument_group('reads release info')
    mutex_group = parser.add_mutually_exclusive_group(required = True)
    mutex_group.add_argument('--working', action = 'store_true', help = 'release currently in database')
    mutex_group.add_argument('--private', action = 'store_true', help = 'release on private ftp')
    mutex_group.add_argument('--public', action = 'store_true', help = 'release on public ftp')
    mutex_group.add_argument('--all-info', action = 'store_true', help = 'displays all release info')
    mutex_group.add_argument('--when', metavar = 'YYYY_MM', help = 'it will return the release date for the given release number')
    mutex_group.add_argument('--delta', default = DELTA, type = int, help = 'interval of days between releases')
    #tells you what the previous release was
    #mutex_group.add_argument('--previous-release', action = 'store_true', help = 'displays all release info')
    #mutex_group.add_argument('--next-release', action = 'store_true', help = 'displays all release info')
    parser.add_argument('--release-date', action = 'store_true', help = 'displays release date')
    parser.add_argument('--release-date-fmt', nargs = '?', help = 'release date format see http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior', const = DATE_FMT_DEFAULT, default = DATE_FMT_DEFAULT)
    #write_group=parser.add_argument_group('updates release info', 'these options require write permission to files in /ebi/uniprot/data/release_info')
    mutex_group = parser.add_mutually_exclusive_group(required = False)
    mutex_group.add_argument('--private-ftp-done', action = 'store_true', help = 'private ftp is done, private is updated')
    mutex_group.add_argument('--copy-db-done', action = 'store_true', help = 'copy of db is done, working is updated, we begin next release cycle')
    mutex_group.add_argument('--public-ftp-done', action = 'store_true', help = 'public ftp is done, updates public with release info of private')
    args = parser.parse_args()

    DELTA = args.delta
    DATE_FMT = args.release_date_fmt

    ## writes to /ebi/uniprot/data/release_info/
    if args.private_ftp_done:
        #read current private
        private = read_release('private')
        private_release_date = read_release_date('private')
        #increase private
        private = increment_release(private)
        private_release_date = increment_release_date(private_release_date, DELTA)
        check(private = private)
        write_release('private', private)
        write_release_date('private', private_release_date)
        sendEmail('$private_release', private)
    elif args.copy_db_done:
        #read current working
        cur_working = read_release('working')
        cur_working_release_date = read_release_date('working')
        next_working = increment_release(cur_working)
        next_working_release_date = increment_release_date(cur_working_release_date, DELTA)
        # check if next release will have shifted date
        historyDict = loadHistory()
        if next_working in historyDict.keys(): next_working_release_date = historyDict.get(next_working)
        #update working with next working, but first check against public
        check_against_public(next_working)
        check(working = next_working)
        write_release('working', next_working)
        write_release_date('working', next_working_release_date)
        sendEmail('$working_release', next_working)
    elif args.public_ftp_done:
        #read current private
        private = read_release('private')
        private_release_date = read_release_date('private')
        check(public = private)
        #update public
        write_release('public', private)
        write_release_date('public', private_release_date)
        #and save it in history
        saveHistory(private, private_release_date)
        sendEmail('$public_release', private)

    release = ''
    release_date = ''
    if args.working:
        release = read_release('working')
        if args.release_date: release_date = read_release_date('working')
        msg = "%s %s" % (release, release_date)
        print(msg.strip())
    elif args.private:
        release = read_release('private')
        if args.release_date: release_date = read_release_date('private')
        msg = "%s %s" % (release, release_date)
        print(msg.strip())
    elif args.public:
        release = read_release('public')
        if args.release_date: release_date = read_release_date('public')
        msg = "%s %s" % (release, release_date)
        print(msg.strip())
    elif args.all_info:
        print('working release:', read_release('working'), read_release_date('working'))
        print('private release:', read_release('private'), read_release_date('private'))
        print('public  release:', read_release('public'), read_release_date('public'))
    elif args.when:
        when(args.when)

