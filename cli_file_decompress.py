#!/usr/bin/env python

import argparse
import os
import sys

from src.compressor import Decompressor as cc


def parse():
    desc = """\
Sliding Window Decompressor by Zijie Wu
Example usage:
    cli_file_decompress book1.txt.s ...
"""

    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", help="Files to decompress", nargs="*", default=sys.stdin.buffer, type=argparse.FileType('rb'))
    argv = parser.parse_args()

    files = argv.files

    return files


def decompress(files):
    if type(files) is list:
        # List of files
        for file in files:
            filename = file.name

            # process file name
            output_file = filename[:-2]

            # compress with hw2
            c = cc(file).run()
            c.write_to_file(output_file)

            # remove original file
            os.remove(filename)
    else:
        # stdin
        c = cc(files).run()
        c.write_to_stdout()


if __name__ == '__main__':
    files = parse()

    decompress(files)
