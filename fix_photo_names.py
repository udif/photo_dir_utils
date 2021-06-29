#!/usr/bin/env python3

#
# Extract creation date & time from JPG / CR2 (Canon RAW) / QuickTime movies and rename files to begin with it
#
import os
import sys
import re
import pprint
import exif
import struct

# Taken from https://raw.githubusercontent.com/Deconimus/quicktime-parser/ec7537c782b8ef4940872c40d25277e6ca180e97/quicktimeparser/parse.py
# But renamed to quicktime_parse.py
from quicktime_parse import *

def get_cr2_date_time( fh ):
    buffer = fh.read(8)
    b_off = 8
    if buffer[0] == ord('I'):
        ul = "<L"
        us = "<H"
    else:
        ul = ">L"
        us = ">H"
    ifd_offset = struct.unpack_from(ul, buffer, 4)[0]
    buffer = fh.read(ifd_offset+2-b_off)
    b_off = ifd_offset+2
    ifd_entries = struct.unpack_from(us, buffer, ifd_offset-8)[0]
    buffer = fh.read(12*ifd_entries)
    b_off += 12*ifd_entries
    for i in range(0, ifd_entries):
        ifd_entry_type = struct.unpack_from(us, buffer, 12*i)[0]
        if ifd_entry_type == 0x132:
            dt_size = struct.unpack_from(ul, buffer, 12*i+4)[0]
            dt_off = struct.unpack_from(ul, buffer, 12*i+8)[0]
    buffer = fh.read(dt_off - b_off)
    buffer = fh.read(dt_size)
    b_off = dt_off + dt_size
    return buffer.decode('iso-8859-1')

pp = pprint.PrettyPrinter(indent=4)

def save_prev_file(name, ext):
    old = ("_old."+ext).join(name.rsplit("."+ext, 1))
    if os.path.isfile(name):
        if os.path.isfile(old):
            os.remove(old)
        os.rename(name, old)

if len(sys.argv) != 2:
        print("""
Usage: makedirslike <photosdir>

This utility takes a directory name containing photos.
It then renames all photos into a canonical name format
containing both date, time and the original name.

""")
        exit()

photosdir  = sys.argv[1]
flat = True

if not os.path.isdir(photosdir):
    print(photosdir, "is not a directory")
    sys.exit(1)

for (root,d_names,f_names) in os.walk(photosdir):
    if not flat:
        print("cd", root)
    for f in f_names:
        fl = f.lower()
        if re.search('^(mvi_|img_|dsc[_f])[\d]{4}\.(jpe?g|cr2|mov|m4v)$', fl):
            p = os.path.join(root, f)
            p_xmp = os.path.splitext(p)[0] + '.xmp'
            with open(p, "rb") as fh:
                if fl.endswith('cr2'):
                    d = get_cr2_date_time(fh)
                elif fl.endswith('mov') or fl.endswith('m4v'):
                    m = Mov(p)
                    m.parse()
                    d = " ".join(m.metadata['creation time'].split()[0:2]).replace('-', ':')
                elif fl.endswith('jpg') or fl.endswith('jpeg'):
                    d = exif.Image(fh).datetime_original
                else:
                    print("Unknown file type for", f)
                    sys.exit(0)
                dt = [dt.split(':') for dt in d.split()]
                new_f = '_'.join((''.join(dts) for dts in dt)) + "_" + f
                new_p = os.path.join(root, new_f)
                new_p_xmp = os.path.splitext(new_p)[0] + '.xmp'
                if flat:
                    print (p, '=>', new_p)
                else:
                    print (f, '=>', new_f)
                if os.path.isfile(p_xmp):
                    if flat:
                        print(p_xmp, '=>', new_p_xmp)
                    else:
                        f_xmp = os.path.splitext(f)[0] + '.xmp'
                        new_f_xmp = os.path.splitext(new_f)[0] + '.xmp'
                        print(f_xmp, '=>', new_f_xmp)
sys.exit(0)
