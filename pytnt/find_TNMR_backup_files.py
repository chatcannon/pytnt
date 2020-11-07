#!/usr/bin/python
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: 2013 Christopher Kerr
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""
There is an option in the TNMR control software to save backup files at
regular intervals during data acquisition, so that in the event of power
failure or system crash only the data acquired since the last backup file is 
lost. These backup files are saved in the same directory as the main file and
have the same name but with a suffix of _N (where N is a decimal number) on
the basename.

It is possible to use a standard find command to find files ending in _N.tnt,
but this will also catch files which just happen to have been given a name
ending in _N, which are not backup files. This script adds some sanity checks
to avoid finding files which look like backup files but actually aren't.
"""

from __future__ import print_function

import sys
import os
import os.path
import re
import subprocess 
from contextlib import contextmanager
import argparse


@contextmanager
def pushdir(dirpath):
    saved_dir = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(saved_dir)


## Functions that define possible actions to take when a file is found


def print_filename(dirpath, fname):
    print(fname)


def print_filepath(dirpath, fname):
    print(os.path.join(dirpath, fname))


def delete(dirpath, fname):
    os.unlink(os.path.join(dirpath, fname))


def delete_svn(dirpath, fname):
    with pushdir(dirpath):
        subprocess.check_call(['svn', 'rm', fname])


def delete_git(dirpath, fname):
    with pushdir(dirpath):
        subprocess.check_call(['git', 'rm', fname])


## Handle command line arguments

parser = argparse.ArgumentParser(description='Find and process TNMR backup files')
parser.add_argument('path_to_search', type=str, default='.')
parser.add_argument('-print', action='append_const',
                    const=print_filepath, dest='actions',
                    help="Print the paths to the backup files found to stdout")
parser.add_argument('-print_basename', action='append_const',
                    const=print_filename, dest='actions',
                    help="Print the basenames of the backup files to stdout")
parser.add_argument('-delete', action='append_const',
                    const=delete, dest='actions',
                    help="Delete all backup files found")
parser.add_argument('-gitrm', action='append_const',
                    const=delete_git, dest='actions',
                    help="Delete backup files using git rm")
parser.add_argument('-svnrm', action='append_const',
                    const=delete_svn, dest='actions',
                    help="Delete backup files using svn rm")
parser.add_argument('--quiet', '-q', action='store_const', dest='log_std',
                    const=open('/dev/null', 'w'), default=sys.stderr,
                    help="Don't print reasons for omitting files")

def main():
    args = parser.parse_args()
    
    if args.actions is None:
        actions = [print_filepath]  # Default action
    else:
        actions = args.actions

    find_TNMR_backup_files(args.path_to_search, actions, args.log_std)


## Search the file system
def find_TNMR_backup_files(path_to_search, actions, log_std):
    for dirpath, dirnames, filenames in os.walk(path_to_search):
        for fname in filenames:
            if re.match('.*\.tnt_\d+\.tnt$', fname):
                for act in actions:
                    act(dirpath, fname)
            elif re.match('.*_\d+\.tnt$', fname):
                base_fname = re.sub('_\d+\.tnt$', '.tnt', fname)
                if base_fname in filenames:
                    my_stat = os.stat(os.path.join(dirpath, fname))
                    base_stat = os.stat(os.path.join(dirpath, base_fname))
                    if my_stat.st_size > base_stat.st_size:
                        print("%s is bigger than %s, keeping" % (fname, base_fname), file=log_std)
                    elif my_stat.st_mtime > base_stat.st_mtime:
                        print("%s is newer than %s, keeping" % (fname, base_fname), file=log_std)
                    
                    ## I had the idea of checking for file age difference but the
                    ## files I have all seem to have much bigger mtime differences
                    ## than would make sense based on when they were acquired.
#                    elif my_stat.st_mtime < (base_stat.st_mtime - 3600 * 24 * 7):
#                        my_mtime = time.gmtime(my_stat.st_mtime)
#                        base_mtime = time.gmtime(base_stat.st_mtime)
#                        print ("%s is more than a week older than %s, keeping" % (fname, base_fname), file=log_std)
#                        print ("%s was last modified at %s" % (fname, time.strftime('%c', my_mtime)), file=sys.stderr)
#                        print ("%s was last modified at %s" % (base_fname, time.strftime('%c', base_mtime)), file=sys.stderr)
                    else:
                        for act in actions:
                            act(dirpath, fname)
                else:
                    print('%s does not have a matching base file %s, keeping' % (fname, base_fname), file=log_std)


if __name__ == '__main__':
    main()
