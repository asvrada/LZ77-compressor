from collections import deque


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
        return 3


class SlidingWindowEncoder:
    def __init__(self):
        self.pointer = Pointer()

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

    def popleft_n(self, queue, n):
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

    def open_file(self, path):
        f = open(path, "rb")
        return f.read()

    def compress(self, text):
        """
        todo: receive filename
        Compress the text using a sliding window
        :param text: the input
        :type text: bytes
        :return: compressed text
        """
        # Store the text into a queue
        text = deque(text)

        """
        1. init sliding window and read ahead buffer
        """
        sliding_window = deque(maxlen=self.pointer.size_sliding_window())
        buffer = deque(maxlen=self.pointer.size_buffer())

        """
        2. init read ahead buffer
        """
        # init read buffer
        buffer.extend(self.popleft_n(text, self.pointer.size_buffer()))

        """
        3. Start the encoding loop
        """
        # The encoded text
        encoded = []

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

            # output this encoding
            # length - min_match
            encoded.append((offset, length - self.pointer.size_min_match()))

            # remove length + 1 element from buffer, put them into sliding window
            sliding_window.extend(self.popleft_n(buffer, length))

            # move following text into buffer
            buffer.extend(self.popleft_n(text, length))

        return encoded

    def compress_to_file(self, input_data, out_file_name):
        """
        Read ASCII file and compress it and output to ASCII file
        :param input_data:
        :type input_data:
        :param out_file_name:
        :type out_file_name:
        :return:
        :rtype:
        """

    def decompress(self, encoded):
        pass
