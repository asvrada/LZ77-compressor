import argparse

from Compressor.compressor import Compressor

parser = argparse.ArgumentParser(description="Sliding Window Compressor by Zijie Wu\nExample usage:\npython ccli.py zip book1.txt compressed.file", formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("ACTION", help="Set program to compress or decompress input file", type=str, choices=["zip", "unzip"], default="zip")
parser.add_argument("files", help="Files to compress or decompress", nargs="*")
parser.add_argument("--size", type=int, help="Assign number of bits to sliding window\n9: 4K, 13: 64K", choices=[9, 13], metavar='size', default=9)

argv = parser.parse_args()

action = argv.ACTION
input_files = argv.files
size = argv.size

c = Compressor(size)

if action == "zip":
    print("Zipping", input_files)
    for each in input_files:
        c.compress_to_file(each, each + ".S")
elif action == "unzip":
    print("Unzipping", input_files)
    for each in input_files:
        c.decompress_to_file(each, each - ".S")
