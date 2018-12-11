from collections import deque

from .utilities import popleft_n, read_from_buffer
from .pointer import Pointer

import sys


class Compressor:
    def __init__(self, buffered_reader, bits_windows=12):
        self.pointer = Pointer(bits_windows)
        self.escape_char = b"\xCC"
        self.content = deque(read_from_buffer(buffered_reader))
        self.result = bytearray()

    def find_match(self, sliding_window, buffer):
        """
        Find a match (both inclusive) longer than SIZE_MIN_MATCH and shorter than SIZE_MAX_MATCH
        The string starts from buffer[0]

        :param sliding_window: The sliding window buffer
        :type sliding_window: deque
        :param buffer: The read ahead buffer
        :type buffer: deque
        :return: A tuple contains (offset, length) or None when there is no match
        :rtype: tuple | None
        """
        size_window = len(sliding_window)
        size_buffer = len(buffer)

        cur_sliding_window = size_window - 1

        # we are scanning from the right of sliding window
        while cur_sliding_window >= 0:

            # no match, move to next
            if sliding_window[cur_sliding_window] != buffer[0]:
                cur_sliding_window -= 1
                continue

            # we might found a match, start matching now
            cur_buffer = 0
            # we don't want to mess cur_sliding_window before finding a solid match
            tmp_sliding_window = cur_sliding_window

            """
            Matching
            """
            # don't go outside of the sliding window and read ahead buffer
            # and keep the length of match less that MAX_LENGTH
            while tmp_sliding_window < size_window and cur_buffer < size_buffer \
                    and cur_buffer < self.pointer.length_longest_match() \
                    and sliding_window[tmp_sliding_window] == buffer[cur_buffer]:
                cur_buffer += 1
                tmp_sliding_window += 1

            """
            End of matching
            """
            # if length < SIZE_MIN_MATCH, ignore this match
            if cur_buffer < self.pointer.length_shortest_match():
                cur_sliding_window -= 1
                continue

            # we find a valid match, now encode it
            offset = len(sliding_window) - (tmp_sliding_window - cur_buffer) - 1
            length = cur_buffer
            return offset, length

        return None

    def compress(self):
        encoded = self.result

        """
        1. init sliding window and read ahead buffer
        """
        sliding_window = deque(maxlen=self.pointer.size_sliding_window())
        buffer = deque(maxlen=self.pointer.size_buffer())

        """
        2. init read ahead buffer
        """
        # fill read ahead buffer
        buffer.extend(popleft_n(self.content, self.pointer.size_buffer()))

        """
        3. Start the encoding loop
        """
        # before start, encode size of sliding window using 1 byte
        encoded.append(self.pointer.bits_offset)

        while len(buffer) > 0:
            result = self.find_match(sliding_window, buffer)

            """
            no match found, simply output without compress/encode
            """
            if result is None:
                # remove one from buffer, put it into sliding window
                head = buffer.popleft()
                sliding_window.append(head)

                # output to encoded
                # escape char
                if head == self.pointer.ESCAPE_CHAR:
                    # \xCC -> \xCC\x00\x00
                    encoded.append(self.pointer.ESCAPE_CHAR)
                    encoded.extend(bytes(b"\x00") * self.pointer.size)
                else:
                    encoded.append(head)

                # read next char from input
                if len(self.content) > 0:
                    buffer.append(self.content.popleft())

                # back to find next match
                continue

            """
            match found, compress/encode it
            """
            offset, length = result

            # output this pointer
            encoded.extend(self.pointer.encode(offset, length))

            # remove number of "length" elements from buffer, put them into sliding window
            sliding_window.extend(popleft_n(buffer, length))

            # move following text into buffer
            buffer.extend(popleft_n(self.content, length))

    def run(self):
        self.compress()
        return self

    def write_to_file(self, output):
        # store the bytearray to file
        with open(output, "wb") as file:
            file.write(self.result)

        return self

    def write_to_stdout(self):
        sys.stdout.buffer.write(self.result)
        return self


class Decompressor:
    def __init__(self, buffered_reader):
        self.content = read_from_buffer(buffered_reader)
        self.pointer = None
        self.result = bytearray()

    def run(self):
        self.decompress()
        return self

    def decompress(self):
        """
        Decompress the compressed data
        """

        # before we start, decode the size of sliding window
        self.pointer = Pointer(self.content[0])

        cur = 1
        while cur < len(self.content):
            head = self.content[cur]
            """
            Decode non-pointers
            """
            if head != self.pointer.ESCAPE_CHAR:
                self.result.append(head)
                cur += 1
                continue

            # If is escaped char
            if sum(self.content[cur + 1: cur + self.pointer.size + 1]) == 0:
                self.result.append(self.pointer.ESCAPE_CHAR)
                cur += self.pointer.size + 1
                continue

            """
            Decode pointer
            """
            barr = bytearray(self.content[cur: cur + self.pointer.size + 1])
            # move cursor to the next position
            cur += self.pointer.size + 1

            # decode the pointer information
            offset, length = self.pointer.decode(barr)
            start = len(self.result) - offset - 1
            end = start + length

            # copy the content from previous location
            self.result.extend(self.result[start:end])

    def write_to_file(self, output):
        # store the bytearray to file
        with open(output, "wb") as file:
            file.write(self.result)

    def write_to_stdout(self):
        sys.stdout.buffer.write(self.result)
