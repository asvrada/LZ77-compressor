import sys
import string

from sliding_window_compressor import SlidingWindowEncoder, Pointer


def print_encoded(encoded):
    print(encoded)


def test_read_file(file_path):
    compressor = SlidingWindowEncoder()
    file_text = compressor.open_file(file_path)

    print("Length before compression:", len(file_text))

    compressed = compressor.compress(file_text)

    print("Length AFTER: ", len(compressed))

    decoded = compressor.decompress(compressed)
    print("Length extracted: ", len(decoded))


def test_simple_input():
    text = string.ascii_lowercase * 3 + "hello world"
    text = text.encode("ascii")

    print("Length before compression:", len(text))

    compressor = SlidingWindowEncoder()
    ret = compressor.compress(text)

    print("Length AFTER: ", len(ret))

    decoded = compressor.decompress(ret)
    print(decoded)


if __name__ == '__main__':
    # test_simple_input()
    test_read_file(sys.argv[1])
