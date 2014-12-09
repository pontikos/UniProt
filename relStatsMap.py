#!/usr/bin/env python
from __future__ import print_function
import argparse
import os.path
import sys
from collections import defaultdict
import utility_arg_parser
import pickle

def isoDate(txt):
    dd, mm, yyyy = txt.split('-')
    months = {'JAN':'01', 'FEB':'02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06',
              'JUL':'07', 'AUG':'08', 'SEP':'09', 'OCT':'10', 'NOV': '11', 'DEC': '12'}
    return "%s-%s-%s" % (yyyy, months.get(mm.upper()), dd)

def parseRL(lista):
    if not lista: return 0
    tmp = ''
    rls = []
    for item in lista:
        if item.endswith('.'):
            rls.append(tmp + item)
            tmp = ''
        else:
            tmp += item + ' '
    return rls

def statsToFlatFile(aDict):
    outContent = ''
    for k, v in aDict.iteritems():
        if k.startswith('$'):
            txt = '%s^%s^\n' % (k, v)
            outContent += txt
        elif k.startswith('@'):
            txt = '%s^%s^\n' % (k, ' '.join([str(x) for x in v]))
            outContent += txt
        elif k.startswith('%'):
            txt = '%s^' % k
            for kk, vv in v.iteritems():
                txt += '%s>%s^' % (kk, vv)
            if not v:
                txt += '^\n'
            else:
                txt += '\n'
            outContent += txt
    return outContent


if __name__ == '__main__':
    # python relStatsMap.py --file test.dat --prev_date 03-May-2011 -t
    #cat test.dat | python relStatsMap.py --prev_date 03-May-2011 -t
    parser = argparse.ArgumentParser()

    parser.add_argument('--prev_date', dest = 'prev_date', help = "previous release date, e.g. 03-May-2011", required = True)
    parser.add_argument('-t', dest = 'txt', help = "returns the results in text format", action = 'store_true')
    input = utility_arg_parser.get_input_source(parser)
    args = parser.parse_args()

    prev_date = isoDate(args.prev_date)
    content = input

    entry = defaultdict(list)
    stats = {}
    cEntry = 0
    cEntryAdded = 0
    cEntryAnnupdated = 0
    cEntryUpdated = 0
    cAmino = 0
    cAminoNew = 0
    cFragments = 0
    longest_len = 0
    shortest_len = None
    cAminoHash = defaultdict(int)
    cAuthor = defaultdict(int)
    cOrganelle = defaultdict(int)
    cOrganism = defaultdict(int)
    cSize = defaultdict(int)
    createdAll = defaultdict(int)
    createdHuman = defaultdict(int)
    classes = ["Mammalia", "Vertebrata", "Fungi", "Insecta", "Nematoda", "Viridiplantae"]
    createdTaxon = {}
    for key in classes:
        createdTaxon[key] = 0
    others = ['unclassified sequences', 'other sequences']
    ocCategories = defaultdict(int)
    lineCountPE = [0, 0, 0, 0, 0, 0]
    lineCount = defaultdict(int)
    lineCountRL = defaultdict(int)
    entryLineCountRL = defaultdict(int)
    exceptCC = ['Copyright', "ENZYME REGULATION", "DEVELOPMENTAL STAGE", "INDUCTION",
                "TISSUE SPECIFICITY", "PTM", "POLYMORPHISM", "DISEASE", "BIOPHYSICOCHEMICAL PROPERTIES",
                "ALTERNATIVE PRODUCTS"]
    lineCountCC = defaultdict(int)
    entryLineCountCC = defaultdict(int)
    exceptDR = ["_HIDDEN_", "OGP", "PhosSite", "MIM"]
    lineCountDR = defaultdict(int)
    entryLineCountDR = defaultdict(int)
    keysFT = ["NON_TER", "CHAIN", "SIGNAL", "TRANSIT"]
    lineCountFT = defaultdict(int)
    entryLineCountFT = defaultdict(int)
    for line in content.xreadlines():
        if line.startswith('//'):
            # reading block finished, process entry and stats
            cre_date, seq_date, ann_date = [isoDate(x.split(',')[0]) for x in entry.get('DT')]
            cEntry += 1
            seq = ''.join(entry.get('')).replace(' ', '')
            entry['SQ'] = seq
            seq_len = len(entry['SQ'])
            for l in list(seq):
                cAminoHash[l] += 1
            cAmino += seq_len
            id = entry.get('ID')[0].split()[0]
            if (cre_date > prev_date):
                cEntryAdded += 1
                cAminoNew += seq_len
            elif (ann_date > prev_date):
                cEntryAnnupdated += 1
                if (seq_date > prev_date):
                    cEntryUpdated += 1
            txtDE = ' '.join(entry.get('DE'))
            if (txtDE.count(' Fragment;') or txtDE.count(' Fragments;')):
                cFragments += 1
            else:
                cSize[seq_len] += 1
            if (seq_len > longest_len):
                longest_len = seq_len
                longest_id = id
            if (not shortest_len or seq_len < shortest_len):
                shortest_len = seq_len
                shortest_id = id
            try:
                for author in ' '.join(entry.get('RA')).replace(';', '').split(','):
                    cAuthor[author.strip().upper()] += 1
            except:
                pass
            lineCountPE[0] += 1
            lineCountPE[int(entry.get('PE')[0].split(':')[0])] += 1
            try:
                #txtOG = ' '.join(entry.get('OG')).strip()[:-1]
                #listOG = ' '.join(entry.get('OG')).replace(' and ', ' ').replace('.', '').split(',')
                #    txtOG = ' '.join(entry.get('OG')).replace(' and ', ' ').replace('.', '')
                #for txtOG in listOG:
                for txtOG in entry.get('OG'):
                    listOG = txtOG.replace('and ', ' ').replace('.', '').split(',')
                    for txt in listOG:
                        if not txt: continue
                        txt = txt.strip()
                        if txt.startswith('Plastid;'):
                            keyOG = txt
                        else:
                            ktxt = txt.split()[0]
                            if not ktxt[0].isupper(): continue
                            keyOG = ktxt
                        cOrganelle[keyOG] += 1
            except:
                pass
            cOrganism[' '.join(entry.get('OS'))[:-1]] += 1
            createdAll[cre_date] += 1
            if (' '.join(entry.get('OC')).count('; Homo.')):
                createdHuman[cre_date] += 1
            txtOC = ' '.join(entry.get('OC'))
            for key in classes:
                key1 = key + ';'
                key2 = key + '.'
                if key1 in txtOC or key2 in txtOC:
                    createdTaxon[key] += 1
            kingdom = txtOC.split(';')[0].replace('.', '')
            if kingdom in others:
                ocCategories['Other'] += 1
            else:
                ocCategories[kingdom] += 1
            linesRL = entry.get('RL')
            rls = parseRL(linesRL)
            lineCount['RL'] += len(rls)
            seenRL = defaultdict(int)
            seenCC = defaultdict(int)
            seenDR = defaultdict(int)
            seenFT = defaultdict(int)
            for rl in rls:
                rl = rl.upper()
                if "Worm Breeder's Gazette".upper() in rl:
                    rlType = "Worm Breeder's Gazette"
                elif rl.startswith('THESIS'):
                    rlType = "Thesis"
                elif rl.startswith('SUBMITTED'):
                    if 'EMBL/' in rl:
                        rlType = "Submitted to EMBL/GenBank/DDBJ"
                    elif 'TrEMBL' in rl:
                        rlType = "Submitted to UniProt/TrEMBL"
                    else:
                        rlType = "Submitted to other databases"
                elif rl.startswith('(IN) '):
                    rlType = "Book citation"
                elif rl.startswith('UNPUBLISHED'):
                    rlType = "Unpublished observations"
                elif rl.startswith('PATENT'):
                    rlType = "Patent"
                else:
                    rlType = "Journal"
                lineCountRL[rlType] += 1
                if not seenRL.get(rlType):
                    seenRL[rlType] += 1
                    entryLineCountRL[rlType] += 1
            for item in entry.get('CC'):
                if item.startswith('-!-'):
                    t = item.split(":")
                    topic = t[0][4:]
                    if topic not in exceptCC:
                        lineCountCC[topic] += 1
                        lineCount['CC'] += 1
                        if not seenCC.get(topic):
                            seenCC[topic] += 1
                            entryLineCountCC[topic] += 1
            try:
                for item in entry.get('DR'):
                    t = item.split(";")
                    dr = t[0]
                    if dr not in exceptDR:
                        lineCountDR[dr] += 1
                        lineCount['DR'] += 1
                        if not seenDR.get(dr):
                            seenDR[dr] += 1
                            entryLineCountDR[dr] += 1
            except:
                #print(entry.get('AC'), file = sys.stderr)
                pass
            try:
                for item in entry.get('FT'):
                    t = item.split()
                    ft = t[0]
                    if ft in keysFT:
                        lineCountFT[ft] += 1
                        lineCount['FT'] += 1
                        if not seenFT.get(ft):
                            seenFT[ft] += 1
                            entryLineCountFT[ft] += 1
            except:
                pass
            # reset entry
            e = entry
            entry = defaultdict(list)
        else:
            key, value = line.split(' ', 1)
            entry[key].append(value.strip())

    stats = {'$cEntry': cEntry, '$cEntryAdded': cEntryAdded, '$cEntryAnnupdated': cEntryAnnupdated,
             '$cEntryUpdated': cEntryUpdated, '$cAmino':cAmino, '$cAminoNew': cAminoNew,
             '$cFragments':cFragments, '$longest_len': longest_len, '$longest_id': longest_id,
             '$shortest_len': shortest_len, '$shortest_id': shortest_id, '%cAminoHash': cAminoHash,
             '%cAuthor':cAuthor, '@lineCountPE': lineCountPE, '%cOrganelle':cOrganelle,
             '%cOrganism':cOrganism, '%cSize': cSize, '%createdAll': createdAll,
             '%createdHuman': createdHuman, "%createdTaxon": createdTaxon,
             '%ocCategories': ocCategories, '%lineCount': lineCount, '%lineCountRL': lineCountRL,
             '%entryLineCountRL': entryLineCountRL, '%entryLineCountCC': entryLineCountCC,
             '%lineCountCC': lineCountCC, '%entryLineCountDR': entryLineCountDR,
             '%lineCountDR': lineCountDR, '%entryLineCountFT': entryLineCountFT,
             '%lineCountFT': lineCountFT}

    outContent = statsToFlatFile(stats)

    #toFile.writelines(outContent)
    if args.txt:
        print(outContent, file = sys.stdout)
    else:
        print(pickle.dumps(stats))
