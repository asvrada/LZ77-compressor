def int2str(number, length):
    """
    Convert number into binary string, and pad with leading 0 if binary string shorter than length

    :param number:
    :type number: int
    :param length:
    :type length: int
    :return: The binary string representation of number
    :rtype: str
    """
    number = "{0:b}".format(number)
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
