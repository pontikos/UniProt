#!/usr/bin/env python
from __future__ import print_function
import argparse
import pickle
from collections import defaultdict
from relStatsMap import statsToFlatFile
import sys
import glob

def parseLongShort():
    olongest_len = stats.get('$longest_len')
    olongest_id = stats.get('$longest_id')
    oshortest_len = stats.get('$shortest_len')
    oshortest_id = stats.get('$shortest_id')
    clongest_len = tmpDict.get('$longest_len')
    clongest_id = tmpDict.get('$longest_id')
    cshortest_len = tmpDict.get('$shortest_len')
    cshortest_id = tmpDict.get('$shortest_id')
    if clongest_len > olongest_len:
        stats['$longest_len'] = clongest_len
        stats['$longest_id'] = clongest_id
    if cshortest_len < oshortest_len:
        stats['$shortest_len'] = cshortest_len
        stats['$shortest_id'] = cshortest_id

if __name__ == '__main__':
    # python relStatsReduce.py -i UP_1_100.stats UP_2_100.stats UP_3_100.stats

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', dest = 'input', help = "file input pickle name ", required = True, nargs = '+')
    args = parser.parse_args()

    stats = {}

    pklFiles = []
    for item in args.input:
        if '*' in item or '?'in item:
            pklFiles += glob.glob(item)
        else:
            pklFiles.append(item)

    #print(len(pklFiles), file = sys.stderr)

    lista = ['$longest_len', '$longest_id', '$shortest_id', '$shortest_len']

    for pklFile in pklFiles:
        tmpDict = pickle.load(open(pklFile, 'rb'))
        #print('ooo', tmpDict.get('@lineCountPE'), tmpDict.get('$cEntry'), tmpDict.get('%lineCountFT'), file = sys.stderr)
        for k, v in tmpDict.iteritems():
            if k.startswith('$'):
                if k not in stats:
                    stats[k] = v
                elif k in lista:
                    continue
                else:
                    stats[k] += v
            if k.startswith('@'):
                if k not in stats:
                    stats[k] = v
                else:
                    for i in range(len(stats[k])):
                        stats[k][i] += v[i]
            if k.startswith('%'):
                if k not in stats:
                    stats[k] = v
                else:
                    for kk, vv in tmpDict[k].iteritems():
                        if kk not in stats[k]:
                            stats[k][kk] = vv
                        else:
                            stats[k][kk] += vv
        parseLongShort()
        #print(stats.get('@lineCountPE'), stats.get('$cEntry'), stats.get('%lineCountFT'), file = sys.stderr)
    out = statsToFlatFile(stats)
    print(out, file = sys.stdout)
