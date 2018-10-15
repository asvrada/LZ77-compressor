from collections import deque


def int2str(number, length):
    number = "{0:b}".format(number)
    # pad leading 0
    return "0" * (length - len(number)) + number


def popleft_n(queue, n):
    """
    Pop n elements from deque

    :param queue: the buffer
    :type queue: deque
    :param n: number of element to pop
    :type n: int
    :return: the popped elements
    :rtype: list[str]
    """
    ret = []

    for _ in range(n):
        if len(queue) == 0:
            break
        ret.append(queue.popleft())

    return ret


class Pointer:
    def __init__(self):
        # Size of each pointer, in bytes
        # size * 8 - 1 = offset + length
        self.size = 3
        # number of bits used to represent offset
        self.bits_offset = 12
        # number of bits used to represent length
        self.bits_length = 11

    def size_sliding_window(self):
        return 2 ** self.bits_offset

    def size_buffer(self):
        return self.size_max_match() + 10

    def size_max_match(self):
        return 2 ** self.bits_length + self.size_min_match()

    def size_min_match(self):
        return self.size + 1

    def encode(self, offset, length):
        """
        todo: bug: hardcoded length
        Encode the offset and length into a pointer of size [self.size] in bytes

        :param offset:
        :type offset: int
        :param length:
        :type length: int
        :return: a bytearray contains the pointer
        :rtype: bytearray
        """
        # map the range of length into correct one
        length -= self.size_min_match()

        # convert number into binary string
        offset = int2str(offset, self.bits_offset)
        length = int2str(length, self.bits_length)

        barr = bytearray([0, 0, 0])

        # flag bit + first 7 bits of offset
        barr[0] = 128 + int(offset[:7], 2)
        # last 5 bits + first 3 bits of length
        barr[1] = int(offset[7:] + length[:3], 2)
        barr[2] = int(length[3:], 2)
        return barr

    def decode(self, arr_bytes):
        """
        Decode pointers from a bytearray

        :param arr_bytes: The bytearray
        :type arr_bytes: bytearray
        :return: offset, length as a tuple
        :rtype: tuple
        """
        # todo: bug: hardcoded length
        arr_binary = [int2str(n, 8) for n in arr_bytes]

        # extract the binary string for offset
        offset = int(arr_binary[0][1:] + arr_binary[1][:5], 2)

        # extract the binary string for length
        length = int(arr_binary[1][5:] + arr_binary[2], 2)

        return offset, length + self.size_min_match()


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
                    and cur_buffer < self.pointer.size_max_match() \
                    and sliding_window[tmp_sliding_window] == buffer[cur_buffer]:
                cur_buffer += 1
                tmp_sliding_window += 1

            # end of matching
            # if length < SIZE_MIN_MATCH, ignore this match
            if cur_buffer < self.pointer.size_min_match():
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
            result = self.find_match(sliding_window, buffer)

            """
            no match found, simply output without compress/encode
            """
            if result is None:
                # remove one from buffer, put it into sliding window
                head = buffer.popleft()
                sliding_window.append(head)

                # output to encoded
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
            if head < 128:
                decode.append(head)
                cur += 1
                continue

            """
            Decode pointer
            """
            barr = bytearray(content[cur: cur + 3])
            cur += 3

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
