#!/usr/bin/env python

import argparse
import os
import sys

from src.compressor import Compressor as cc


def parse():
    desc = """\
Sliding Window Compressor by Zijie Wu
Example usage:
    cli_file_compress book1.txt ...
"""

    parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", help="Files to compress", nargs="*", default=sys.stdin.buffer, type=argparse.FileType('rb'))
    parser.add_argument("--size", type=int, help="Set number of bits to sliding window\nOptions [DEFAULT]9: 4K, 13: 64K", choices=[9, 13], metavar='size', default=9)
    argv = parser.parse_args()

    files = argv.files
    size = argv.size

    return files, size


def compress(files, size):
    if type(files) is list:
        # List of files
        for file in files:
            filename = file.name

            # generate new file name
            output_file = filename + ".s"

            # compress
            c = cc(file, size).run()
            c.write_to_file(output_file)

            # remove original file
            os.remove(filename)
    else:
        # stdin
        c = cc(files, size).run()
        c.write_to_stdout()


if __name__ == '__main__':
    files, size = parse()

    compress(files, size)
