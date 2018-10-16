from Compressor.compressor import Compressor
import argparse

parser = argparse.ArgumentParser(description="Sliding Window Compressor by Zijie Wu\nExample usage:\npython ccli.py zip book1.txt compressed.file", formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("ACTION", help="Set program to compress or decompress input file", type=str, choices=["zip", "unzip"], default="zip")
parser.add_argument("input", type=str, help="Path to input file")
parser.add_argument("output", type=str, help="Path to output the result")

argv = parser.parse_args()
input_file = argv.input
output_file = argv.output

if argv.ACTION == "zip":
    print("Zipping", input_file, output_file)
    c = Compressor().compress_to_file(input_file, output_file)
elif argv.ACTION == "unzip":
    print("Unzipping", input_file, output_file)
    c = Compressor().decompress_to_file(input_file, output_file)
