from collections import deque


class SlidingWindowEncoder:
    def __init__(self):
        # Size of sliding window, in bytes
        self.SIZE_SLIDING_WINDOW = 4081
        # length of max match, in bytes
        self.SIZE_MAX_MATCH = 17
        # Length of min match, in bytes
        self.SIZE_MIN_MATCH = 3
        # Length of the buffer
        self.SIZE_BUFFER = 256

    def find_match(self, sliding_window, buffer):
        """
        Find a match (both inclusive) longer than SIZE_MIN_MATCH and shorter than SIZE_MAX_MATCH
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

            # matching
            while tmp_sliding_window < size_window and cur_buffer < size_buffer and sliding_window[tmp_sliding_window] == buffer[cur_buffer]:
                cur_buffer += 1
                tmp_sliding_window += 1

            # end of matching
            # if length < SIZE_MIN_MATCH, ignore this match
            # todo: if length > SIZE_MAX_MATCH
            if cur_buffer < self.SIZE_MIN_MATCH:
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

    def compress(self, text):
        """
        Compress the text using a sliding window
        :param text: the input
        :type text: string
        :return: compressed text
        """

        text = deque(text)

        """
        1. init sliding window and read ahead buffer
        """
        sliding_window = deque(maxlen=self.SIZE_SLIDING_WINDOW)
        buffer = deque(maxlen=self.SIZE_BUFFER)

        """
        2. init read ahead buffer
        """
        # init read buffer
        buffer.extend(self.popleft_n(text, self.SIZE_BUFFER))

        """
        3. Start the encoding loop
        """
        # The encoded text
        encoded = []

        while len(buffer) > 0:
            print(len(text))
            result = self.find_match(sliding_window, buffer)

            # no match found, simply output without compress/encode
            if result is None:
                # remove one from buffer, put it into sliding window
                head = buffer.popleft()
                sliding_window.append(head)

                # output to encoded
                encoded.append(head)

                # read next char from input
                if len(text) <= 0:
                    continue

                buffer.append(text.popleft())
                continue

            # match found, compress/encode it
            offset, length = result
            # todo: get rid of next char
            next_char = buffer[length] if length < len(buffer) else ""

            # output this encoding
            encoded.append((offset, length, next_char))

            # remove length + 1 element from buffer, put them into sliding window
            sliding_window.extend(self.popleft_n(buffer, length + 1))

            # move text into buffer
            buffer.extend(self.popleft_n(text, length + 1))

        return encoded

    def decompress(self, encoded):
        pass
