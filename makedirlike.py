#!/usr/bin/env python3

import os
import sys
import re
import pprint
import argparse

parser = argparse.ArgumentParser(description="""
This utility takes two lists of files, as produced by xxh128 or md5sum.
The files are expected to be relative, i.e. all files starts at "./..."
For every file in the <dst> file whose hash matches a file from <src>,
The file is moved within <dstdir> from the relative path of <dstfile>
to the relative path of <srcfile> inside <dstdir>.
""")
#parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true", type=int)
parser.add_argument("srchash", metavar="srchashfile", type=str, nargs=1, help="name of hash file crated by md5sum, sha1sum, xxh128sum or others")
parser.add_argument("dsthash", metavar="dsthashfile", type=str, nargs=1, help="name of hash file crated by md5sum, sha1sum, xxh128sum or others")
parser.add_argument("destdir", metavar="destdir", type=str, nargs=1, help="name of hash file crated by md5sum, sha1sum, xxh128sum or others")
#parser.add_argument("-D", "--no-dup-warn", action="store_true", help="do not warn when all files with the same hash are premarke as duplicates")
#parser.add_argument("-O", "--no-orig-warn", action="store_true", help="do not warn when more than one file with the same hash is marked as an original")
#parser.add_argument("-q", "--quiet", action="store_true", help="quiet mode - only warn if all dupes or if more than one orig")
#parser.add_argument("-f", "--dup-file", nargs=1, metavar='dupfile', type=str, help="input file containing duplicate dirs, one per line")
args = parser.parse_args()

pp = pprint.PrettyPrinter(indent=4)

def save_prev_file(name, ext):
    old = ("_old."+ext).join(name.rsplit("."+ext, 1))
    if os.path.isfile(name):
        if os.path.isfile(old):
            os.remove(old)
        os.rename(name, old)

srcfile  = args.srchash[0]
dstfile  = args.dsthash[0]
dstdir  = args.destdir[0]

if not os.path.isfile(srcfile):
    print(srcfile, "is not a file")
    sys.exit(1)
if not os.path.isfile(dstfile):
    print(dstfile, "is not a file")
    sys.exit(1)
if not os.path.isdir(dstdir):
    print(dstdir, "is not a directory")
    sys.exit(1)

file={}
hash = {}
# everything matching this will be considered the 'dup' that needs to be removed
# any duplicate not found in dup_pat will raise an error
dup_pat = ("./image_library_four","./pictures", "./fuji-xp60", "./holland_2015/canon")
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
                    print((f,ext), "is dup")
                    break
            else:
                if orig:
                    print("Error, more than one original found in:\n", files)
                    break
                orig = True
                continue
        if not ignore and not orig:
            print("One dup must be original! :\n", files)
print("""
Dups
----
""")            
pp.pprint(dups)