#!/usr/bin/env python3

import os
import sys
import re
import pprint
import argparse

parser = argparse.ArgumentParser(description="""
This utility takes a hash file list, as produced by xxh128 or md5sum.
It then groups the files by hash value, and makes sure there is only one file for each hash.
If there is more than one file per hash, it must be on a preapproved "dupes" directory list.
The files are expected to be relative, i.e. all files starts at "./..."
It also makes sure that no file appears only in the "dupes" lists.
Finally, it prepares a list of dupes top be deleted.
""")
#parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", type=int)
parser.add_argument("hashfile", metavar="hashfile", type=str, nargs=1, help="name of hash file crated by md5sum, sha1sum, xxh128sum or others")
parser.add_argument("-D", "--no-dup-warn", action="store_true", help="do not warn when all files with the same hash are premarke as duplicates")
parser.add_argument("-O", "--no-orig-warn", action="store_true", help="do not warn when more than one file with the same hash is marked as an original")
parser.add_argument("-q", "--quiet", action="store_true", help="quiet mode - only warn if all dupes or if more than one orig")
parser.add_argument("-f", "--dup-file", nargs=1, metavar='dupfile', type=str, help="input file containing duplicate dirs, one per line")
args = parser.parse_args()

pp = pprint.PrettyPrinter(indent=4)

def save_prev_file(name, ext):
    old = ("_old."+ext).join(name.rsplit("."+ext, 1))
    if os.path.isfile(name):
        if os.path.isfile(old):
            os.remove(old)
        os.rename(name, old)

srcfile  = args.hashfile[0]

if not os.path.isfile(srcfile):
    print(srcfile, "is not a file")
    sys.exit(1)

file={}
hash = {}
# everything matching this will be considered the 'dup' that needs to be removed
# any duplicate not found in dup_pat will raise an error
dup_pat = tuple()
if args.dup_file:
    with open(args.dup_file[0]) as fh:
        dup_pat = tuple(s.rstrip('\n') for s in fh.readlines())

dups = []
with open(srcfile) as f:
    frl = f.readlines()
    # index files by hashes (1->many) and hashes by files (1->1)
    for l in frl:
        m = re.search('(\S+)\s+(.*)', l)
        h = m.group(1)
        fn = m.group(2)
        (f, ext) = os.path.splitext(fn)
        file[(f, ext)] = h
        if h in hash:
            hash[h].append((f,ext))
        else:
            hash[h] = [(f,ext)]
    # check if file appear in potential duplication patterns
    for files in hash.values():
        if len(files) == 1:
            continue
        #print(files)
        orig = False
        ignore = False
        for (f,ext) in files:
            f_l = f.lower()
            if ext.lower() == '.xmp':
                ignore = True
                break
            for pat in dup_pat:
                if f_l.startswith(pat):
                    dups.append((f,ext))
                    if not args.quiet:
                        print((f,ext), "is dup")
                    break
            else:
                if orig:
                    if not args.no_orig_warn:
                        print("Error, more than one original found in: ", files)
                    break
                orig = True
                continue
        if not ignore and not orig:
            if not args.no_dup_warn:
                print("One dup must be original! :", files)
if not args.quiet:
    print("""
Dups
----
""")            
    pp.pprint(dups)