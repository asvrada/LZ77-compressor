from collections import deque

from .utilities import popleft_n
from .pointer import Pointer


class Compressor:
    """
    A compressor that uses sliding window to compress any binary file
    """

    def __init__(self, window_size=12):
        """
        Constructor
        todo: variable window size

        :param window_size: Number of bits of sliding window
        :type window_size: int
        """
        self.pointer = Pointer()
        self.escape_char = b"\xCC"

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

    def compress(self, content):
        """
        Compress the content using a sliding window

        :param content: the input to compress
        :type content: bytes
        :return: compressed content
        :rtype: bytearray
        """
        # Store the text into a queue
        text = deque(content)

        """
        1. init sliding window and read ahead buffer
        """
        sliding_window = deque(maxlen=self.pointer.size_sliding_window())
        buffer = deque(maxlen=self.pointer.size_buffer())

        """
        2. init read ahead buffer
        """
        # fill read ahead buffer
        buffer.extend(popleft_n(text, self.pointer.size_buffer()))

        """
        3. Start the encoding loop
        """
        encoded = bytearray()

        while len(buffer) > 0:
            # print progress
            tmp_total = len(content)
            tmp_current = tmp_total - len(text)
            print("{:.1f}%".format(float(tmp_current) / tmp_total * 100))

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
                    encoded.extend(bytes(b"\xCC\x00\x00"))
                else:
                    encoded.append(head)

                # read next char from input
                if len(text) > 0:
                    buffer.append(text.popleft())
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
            buffer.extend(popleft_n(text, length))

        return encoded

    def compress_to_file(self, input_file, out_file):
        with open(input_file, "rb") as file:
            contents = file.read()

        barr = self.compress(contents)

        # store the bytearray to file
        with open(out_file, "wb") as file:
            file.write(barr)

    def decompress(self, content):
        """
        Decompress the compressed data

        :param content: The input
        :type content: bytes
        :return: The decompressed data
        :rtype: bytearray
        """
        decode = bytearray()

        cur = 0
        while cur < len(content):
            head = content[cur]
            """
            Decode non-pointers
            """
            if head != self.pointer.ESCAPE_CHAR:
                decode.append(head)
                cur += 1
                continue

            # Is escaped char
            if content[cur + 1] == 0 and content[cur + 2] == 0:
                decode.append(self.pointer.ESCAPE_CHAR)
                cur += 3
                continue

            """
            Decode pointer
            """
            barr = bytearray(content[cur: cur + self.pointer.size + 1])
            cur += self.pointer.size + 1

            offset, length = self.pointer.decode(barr)
            start = len(decode) - offset - 1
            end = start + length

            decode.extend(decode[start:end])

        return decode

    def decompress_to_file(self, input_file, output_file):
        """
        Decompress the input file and output to file

        :param input_file:
        :type input_file: str
        :param output_file:
        :type output_file: str
        """
        with open(input_file, "rb") as file:
            content = file.read()

        decoded = self.decompress(content)

        with open(output_file, "wb") as file:
            file.write(decoded)
