import functools
from collections import namedtuple


WHITE = 1
NONE = 0
BLACK = -1


class IllegalPositionError(Exception): pass


class Position(object):

    __slots__ = ('index',)

    @classmethod
    def make(cls, incoming):
        if isinstance(incoming, cls):
            return incoming
        try:
            rank_index, file_index = incoming
        except:
            return cls(incoming)
        else:
            return cls.from_rank_file(rank_index, file_index)


    @classmethod
    def src_dst_provide_position(cls, function):
        @functools.wraps(function)
        def wrapped(self, incoming_src, incoming_dst, *args, **kwargs):
            return function(self, cls.make(incoming_src), cls.make(incoming_dst), *args, **kwargs)
        return wrapped


    @classmethod
    def provide_position(cls, function):
        @functools.wraps(function)
        def wrapped(self, incoming, *args, **kwargs):
            return function(self, cls.make(incoming), *args, **kwargs)
        return wrapped

    @classmethod
    def from_rank_file(cls, rank_index, file_index):
        if rank_index < 0 or rank_index > 7 or file_index < 0 or file_index > 7:
            raise IllegalPositionError()
        cls(rank_index * 8 + file_index)

    def __init__(self, index):
        self.index = index

    @property
    def rank_index(self):
        return (self.index & ~7) >> 3

    @property
    def file_index(self):
        return self.index & 7

    def replace(self, rank_index=None, file_index=None):
        if rank_index is None:
            rank_index = self.rank_index
        if file_index is None:
            file_index = self.file_index

        return self.from_rank_file(rank_index, file_index)

    def delta(self, rank_delta=None, file_delta=None):
        if rank_delta is None:
            rank_delta = 0
        if file_delta is None:
            file_delta = 0

        return self.from_rank_file(self.rank + rank_delta, self.file + file_delta)


_bool_or_none_to_color_map = {
	True: WHITE,
	False: BLACK,
	None: NONE
}


PromotionMoveInfo = namedtuple('MoveInfo', ['source', 'destination', 'promotion'])
MoveInfo = functools.partial(PromotionMoveInfo, promotion=None)


def make_eight(item):
	return [item for _ in range(8)]


def opponent_of(color):
	return color * -1


class ActiveColorError(Exception): pass
class IllegalMoveError(Exception): pass
class IllegalSquareError(Exception): pass
class InvalidNotationError(Exception): pass
class PieceNotFoundError(Exception): pass


def listify(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        return list(function(*args, **kwargs))