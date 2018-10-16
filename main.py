import string
import sys

from Compressor.compressor import Compressor


def open_file(file):
    with open(file, "rb") as f:
        return f.read()


def test_read_file(file_path):
    compressor = Compressor()

    file_text = open_file(file_path)

    print("Length before compression:", len(file_text))

    compressed = compressor.compress(file_text)
    print("Length AFTER: ", len(compressed))

    decoded = compressor.decompress(compressed)
    print("Length extracted: ", len(decoded))


def test_simple_input():
    text = string.ascii_lowercase[:4] * 3
    text = text.encode("ascii")

    print("Length before compression:", len(text))

    compressor = Compressor()
    ret = compressor.compress(text)
    print("Length AFTER: ", len(ret))

    decoded = compressor.decompress(ret)
    print(decoded)


def test_escape():
    text = bytes(b"\xCC\xFF\xCC\xFF\xCC\xFF\xCC\xFF\xCC\xFF\xCC\xFF\xCC\xFF")

    compressor = Compressor()
    ret = compressor.compress(text)

    decoded = compressor.decompress(ret)


if __name__ == '__main__':
    c = Compressor(16)
    c.compress_to_file("test/aaaREADME.txt", "out/output.txt")
    c.decompress_to_file("out/output.txt", "out/decoded.txt")

