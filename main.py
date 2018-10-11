import sys

from sliding_window_compressor import SlidingWindowEncoder


def open_file(file_path):
    file = open(file_path, "r")
    return file.read()


def test_read_file(file_path):
    file_text = open_file(file_path)
    ret = SlidingWindowEncoder().compress(file_text)

    print("Encoded: \n", ret)


def test_simple_input():
    text1 = "ABCDEFGHI" * 3

    ret = SlidingWindowEncoder().compress(text1)
    print(ret)


if __name__ == '__main__':
    test_simple_input()
    # test_read_file(sys.argv[1])
