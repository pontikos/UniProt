# *************************************************************
#
# $Source: /ebi/cvs/seqdb/sptrembl/src/python/tools/mapreduce.py,v $
# $Revision: 1.10 $
# $State: Exp $
# $Date: 2011/09/14 16:09:57 $
# $Author: pontikos $
#
# $Log: mapreduce.py,v $
# Revision 1.10  2011/09/14 16:09:57  pontikos
# *** empty log message ***
#
# Revision 1.9  2011/08/17 12:19:28  awilter
# aesthetic
#
# Revision 1.8  2011/08/17 11:01:01  awilter
# Modifications to allow mapreduce to work the scripts needed for writeStats.sh
#
# option 'nocat'
#
# Revision 1.7  2011/08/10 09:18:05  pontikos
# *** empty log message ***
#
# Revision 1.6  2011/05/26 17:00:51  pontikos
# add check for reduce step
#
# Revision 1.5  2011/05/09 12:18:24  pontikos
# use subprocess instead of threads
#
# Revision 1.4  2011/03/31 14:17:39  pontikos
# *** empty log message ***
#
# Revision 1.3  2011/03/31 13:37:41  pontikos
# *** empty log message ***
#
# Revision 1.2  2011/02/28 12:47:30  pontikos
# *** empty log message ***
#
# Revision 1.1  2011/02/25 10:02:20  pontikos
# *** empty log message ***
#
# Revision 1.5  2011/02/22 18:38:51  pontikos
# python tools to parse FF and distribute jobs on cluster
#
# Revision 1.4  2011/01/06 18:02:53  pontikos
# distribute-ff.py: fix lsf log file
#
# Revision 1.3  2011/01/06 16:56:11  pontikos
# use absolute paths to input and output files
#
#
# *************************************************************
from __future__ import print_function
import argparse
import os.path
import sys
from mmap import mmap
import time
from multiprocessing import Process
import subprocess

usage_example = """
For example in order to grep all AC lines in uniprot_trembl.dat one could do:

python mapreduce.py --infile uniprot_trembl.dat --reducedfile uniprot_trembl.ac_lines --map "grep ^AC" --reduce "cat" --slices 60

python mapreduce.py --infile uniprot_trembl.dat --map "python $CVS/src/python/tools/ffparser.py" --slices 100

    """

parser = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, epilog = usage_example)

#compulsory arguments
parser.add_argument('--infile', dest = 'infile', help = "filename to read from.", required = True)
parser.add_argument('--slices', dest = 'slices', help = "number of slices to distribute", type = int, required = True)
parser.add_argument('--separator', dest = 'separator', help = "record sepator", default = "//\n")
#map arguments
map_options = parser.add_argument_group(title = 'map options')
map_options.add_argument('--map', dest = 'map', help = "command to run on all subfiles. Subfiles get created in output dir of reducedfile if specified", default = "cat")
map_options.add_argument('--noreadchunk', dest = 'readchunk', action = 'store_false', help = "provided your map command understands the --file_slice parameter, do not pipe output of readchunk to map command but use parameter instead", default = True)
map_options.add_argument('--map_jobname', dest = 'map_jobname', help = "jobname to use when submitting map jobs with bsub.", default = 'MAP', required = False)
map_options.add_argument('--map_filename', dest = 'map_filename', help = "filename of subfiles. If none specified will use that of reducedfile. If no reducedfile specified then will use that of infile.", required = False)
map_options.add_argument('--map_ext', dest = 'map_ext', help = "extension of subfiles. If none specified will use that of reducedfile. If no reducedfile specified then will use that of infile.", required = False)
#reduce arguments
reduce_options = parser.add_argument_group(title = 'reduce options')
reduce_options.add_argument('--reduce', dest = 'reduce', help = "command to assemble all subfiles back into reduce file.")
reduce_options.add_argument('--reducedfile', dest = 'reducedfile', help = "Filename of the reduce output.")
reduce_options.add_argument('--remove_subfiles', dest = 'remove_subfiles', help = "Remove subfiles after reduce.", action = 'store_true', default = False)
reduce_options.add_argument('--nocat', dest = 'nocat', action = 'store_true', help = "it won't cat the subfiles before doing the reduce.")

args = parser.parse_args()

#either both true or both false
if (not args.reduce or not args.reducedfile) and (args.reduce or args.reducedfile):
    parser.print_usage()
    print('both reduce and reducedfile must be specified')
    sys.exit(1)

if args.reduce:
    outfilename_base, outfilename, = os.path.split(args.reducedfile)
    if not outfilename_base:
        outfilename_base = '.'
    out_stem, out_ext, = os.path.splitext(outfilename)
else:
    outfilename_base, outfilename, = os.path.split(args.infile)
    outfilename_base = '.'
    out_stem, out_ext, = os.path.splitext(outfilename)

if args.map_ext: out_ext = args.map_ext

if args.map_filename: out_stem = args.map_filename

def bsub(logfile = '', cmd = None, jobname = '', blocking = True, big = False):
    if logfile:
        logfile = '-o %s' % logfile
    else:
        logfile = ''
    if jobname:
        jobname = '-J "%s"' % jobname
    else:
        jobname = ''
    if blocking:
        #if you use -K it will try to read from stdin
        blocking = '-I'
    else:
        blocking = ''
    if big:
        big = '-M 16896 -R "rusage[mem=16896]"'
    else:
        big = ''
    cmd = 'bsub {blocking} {log} -q production -P prod {big} {jobname} "{cmd}"'.format(blocking = blocking, log = logfile, big = big, jobname = jobname, cmd = cmd)
    print(cmd)
    returncode = subprocess.call(cmd, shell = True)
    print(returncode)
    if returncode != 0:
        sys.exit(returncode)
        raise 'hell'

slice_filenames = []

def bsub_map():
    print('distribute', args.map, 'on', args.infile, 'into', args.slices, 'slices')
    if args.reducedfile: print('sending output to', args.reducedfile)
    f = open(args.infile, 'r+b')
    m = mmap(f.fileno(), 0)
    s = len(m)
    print(args.infile, 'is', s, 'bytes', s * 1e-9, 'gigabytes')
    # uniprot entry separator is "//" in FF format
    l = [m.find(args.separator, x) + len(args.separator) for x in [x * s / args.slices for x in range(1, args.slices)]]
    print(len(l), 'splits')
    l2 = [0] + l
    l = l + [s]
    slices = map(lambda x, y: (x, y), l2, l)
    print(len(slices), 'slices')
    print(time.time())
    workers = []
    #logfile='%sdistribute-ff_%d_%s_%s.log'%(outfilename_base, n, filename.split('/')[-1], outfilename,)
    for (i, p) in enumerate(slices):
        i += 1
        slice_length = p[1] - p[0]
        slice_filename = os.path.sep.join([outfilename_base, '%s_%d_%d%s' % (out_stem, i, args.slices, out_ext)])
        slice_filenames.append(slice_filename)
        #reads a chunk of the infile line by line
        if args.readchunk:
            readchunk = "python $CVS_RO/src/python/tools/readchunk.py -f {infile} -s {start} -e {end} | ".format(infile = args.infile, start = p[0], end = p[1])
            file_slice = ''
        else:
            readchunk = ''
            file_slice = "--file_slice {infile}:{start}-{end}".format(infile = args.infile, start = p[0], end = p[1])
        w = Process(target = bsub, kwargs = {'jobname':'%s_%d' % (args.map_jobname, i), 'cmd':'%s %s %s > %s' % (readchunk, args.map, file_slice, slice_filename,), 'blocking':True})
        workers.append(w)
        w.start()
        #print( workers )
        #sleep not to overload submission queue
        time.sleep(1)
    #time.sleep(5)
    #blocking until all threads have returned
    #this could be improved we could already start
    #concatenating files while we wait for others threads
    #to return
    print('joining')
    for w in workers:
        w.join()
        print(w)
        if w.exitcode:
            sys.stderr.write(str(w))
            sys.stderr.write(str(w.exitcode))
            w.terminate()
            sys.exit(w.exitcode)
    #time.sleep(5)
    print('finished')
    print([w.is_alive() for x in workers])
    del workers
    print(time.time())

bsub_map()

#reduce step
def reduce():
    if args.nocat:
        w = Process(target = bsub, kwargs = {'cmd':'%s %s > %s' % (args.reduce, ' '.join(slice_filenames), args.reducedfile,), 'blocking':True, 'jobname':'REDUCE', 'big':True})
    else:
        w = Process(target = bsub, kwargs = {'cmd':'cat %s | %s > %s' % (' '.join(slice_filenames), args.reduce, args.reducedfile,), 'blocking':True, 'jobname':'REDUCE', 'big':True})
    w.start()
    w.join()
    if w.exitcode:
        print('REDUCE_ERROR')
        print(w.exitcode)
        sys.exit(w.exitcode)
    print(time.time())
    if (args.remove_subfiles):
        # final rm of all temp output files
        w = Process(target = bsub, kwargs = {'cmd':'rm %s' % ' '.join(slice_filenames), 'blocking':True, 'jobname':'FINAL_RM', 'big':True})
        w.start()

if args.reduce: reduce()

print(time.time())


