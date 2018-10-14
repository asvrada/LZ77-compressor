import sys
import string

from sliding_window_compressor import SlidingWindowEncoder


def print_encoded(encoded):
    ret = list(map(lambda x: chr(x) if type(x) == int else x, encoded[:100]))
    print(ret)


def test_read_file(file_path):
    compressor = SlidingWindowEncoder()
    file_text = compressor.open_file(file_path)
    ret = SlidingWindowEncoder().compress(file_text)

    print_encoded(ret)


def test_simple_input():
    text = string.ascii_lowercase * 3
    text = text.encode("ascii")

    ret = SlidingWindowEncoder().compress(text)
    print_encoded(ret)


if __name__ == '__main__':
    test_simple_input()
    # test_read_file(sys.argv[1])
