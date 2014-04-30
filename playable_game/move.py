from . import common


class Move(object):

    @common.Position.src_dst_provide_position
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination