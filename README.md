Media cataloging tools
======================
This project contains several tools I needed for managing my Photos and movies directory

detect_dupes.py
---------------
Over the years, some of the files got duplicated when I copied files or directories into sepate dirs
when I worked on them, collecting files from several places into one dir.
This utility will find all the duplicate copies, and allows you to mark in an external file which directories
are containing duplicate files and can be removed.
### Features:
* Warn if you define too many duplicate dirs, detected when a file does not have any non dupe copy.
* Warn you when a file has more than one copy not marked as dupe.
* Make sure 'xmp' files are attached to their respective media file. 'xmp' are external tag files, allowing you to catalog your photos without modifying an original image file you already have backed up in the cloud.

This utility relies on an external report file containing hash values for each file.
Such a file can be produced by any hash utility such as md5sum, sha1sum, sha256sum, xxh128sum, etc.

To create a file list:

cd photo_directory
find . -type f -exec xxh128sum -q '{}' ';' |& tee ~/xxh128sumq_list

fix_photo_names.py
------------------
This utility moves all media files into predefined locations in the following template:
YYYY/YYYYMMDD_HHMMSS_<orig_name>
The datestamp is based on the creation date, which is extracted from file headers or EXIF for JPG, CR2, or quicktime files.

It is **strongly** advised to run this only after all dupes have been resolved by 'detect_dupes.py' above as otherwise it may cause more than one file to be mapped to the same location.

makedirlike.py
--------------
Once your 'reference' directory is ready, you may wish to apply the same naming on other directories containing older backups.
All you need is to prepare a hashfile for the other directory, and run the scritpt with both lists.
The script will match files with identical hashes and move them to the same relative location in the destination directory.
