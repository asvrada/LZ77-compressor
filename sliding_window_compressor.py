class Pointer:
    """
    This class presents pointer if the word occurs in the sliding window
    ASCII, one byte
    if p < 256, then it represents the actual byte value(text)
    if p >= 256,
        from left -> right

    """
    def __init__(self):
        # relative position in byte
        self.offset = 0
        # length in byte
        self.length = 0
        pass

    def set_offset(self, pos):
        pass

    def set_length(self, length):
        pass

    def get_offset(self):
        pass

    def get_length(self):
        pass

def sliding_window_compress(text):
    """
    Each point is two bytes long
    :param text:
    :return:
    """
    pass

def sliding_window_decompress(encoded):
    pass