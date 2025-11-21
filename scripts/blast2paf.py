#!/usr/bin/env python3

import argparse
import sys

parser = argparse.ArgumentParser(description= 'Convert tabular blast output to paf format. See the code itself for expected columns from blast')
parser.add_argument('blast', help= 'Blast output to be converted [%(default)s]', default= '-', nargs= '?')
parser.add_argument('--version', '-v', action= 'version', version= '%(prog)s 0.2.0')
args = parser.parse_args()

close_fin = False
if args.blast == '-':
    blast = sys.stdin
else:
    blast = open(args.blast)
    close_fin = True

for line in blast:
    if line.startswith('#'):
        continue
    # These are the columns we expect in blast input
    [qaccver, qlen, qstart, qend, sstrand, saccver, slen, sstart, send, nident, pident] = line.strip().split('\t')
    qlen = int(qlen)
    qstart = int(qstart)
    qend = int(qend)
    slen = int(slen)
    sstart = int(sstart)
    send = int(send)
    nident = int(nident)
    
    if ((qstart < qend) and (sstart < send)) or ((qstart > qend) and (sstart > send)):
        sstrand = '+'
    else:
        sstrand = '-'

    if qstart > qend:
        _qstart = qend
        _qend = qstart
        qstart = _qstart
        qend = _qend
    if sstart > send:
        _sstart = send
        _send = sstart
        sstart = _sstart
        send = _send
    qstart -= 1
    sstart -= 1
    aln_length = qend - qstart
    mapq = 255
    out = [qaccver, qlen, qstart, qend, sstrand, saccver, slen, sstart, send, nident, aln_length, mapq]
    out = '\t'.join([str(x) for x in out])
    print(out)
if close_fin:
    blast.close()

