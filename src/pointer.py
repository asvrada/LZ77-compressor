from .utilities import int2str
import math


class Pointer:
    def __init__(self, bits_offset=12):
        bits_offset = max(10, bits_offset)

        self.ESCAPE_CHAR = int.from_bytes(b"\xCC", byteorder="big")

        # Size of the entire pointer, in bytes, NOT including escape character
        # size * 8 = offset + length
        self.size = max(2, math.ceil((bits_offset + 4) / 8))
        # number of bits used to represent offset
        self.bits_offset = bits_offset
        # number of bits used to represent length
        self.bits_length = self.size * 8 - self.bits_offset

    def size_sliding_window(self):
        """
        Size of sliding window in bytes
        """
        return 2 ** self.bits_offset

    def size_buffer(self):
        """
        Size of read ahead buffer in bytes
        """
        return self.length_longest_match() + 10

    def length_longest_match(self):
        """
        Length of the longest match possible (inclusive)
        :return:
        :rtype:
        """
        return 2 ** self.bits_length + self.length_shortest_match() - 1

    def length_shortest_match(self):
        """
        Length of the shortest match possible (inclusive)
        :return:
        :rtype:
        """
        # +2 to compensate for the escape character
        return self.size + 2

    def encode(self, offset, length):
        """
        Encode the offset and length into a pointer of size [self.size] in bytes

        :param offset:
        :type offset: int
        :param length:
        :type length: int
        :return: a bytearray contains the pointer
        :rtype: bytearray
        """
        # map the range of length into correct one
        length -= self.length_shortest_match()

        # convert number into binary string
        bstr = int2str(offset, self.bits_offset) + int2str(length, self.bits_length)

        barr = bytearray([0] * (self.size + 1))

        barr[0] = self.ESCAPE_CHAR
        for i in range(1, len(barr)):
            barr[i] = int(bstr[(i - 1) * 8:i * 8], 2)

        return barr

    def decode(self, arr_bytes):
        """
        Decode pointers from a bytearray

        :param arr_bytes: The bytearray
        :type arr_bytes: bytearray
        :return: offset, length as a tuple
        :rtype: tuple
        """
        bstr = "".join([int2str(n, 8) for n in arr_bytes[1:]])

        offset = int(bstr[:self.bits_offset], 2)
        length = int(bstr[self.bits_offset:], 2)

        return offset, length + self.length_shortest_match()
