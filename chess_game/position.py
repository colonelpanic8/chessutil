from __future__ import absolute_import
import functools

from . import common


class Position(object):

    __slots__ = ('index',)

    @classmethod
    def make(cls, incoming):
        if isinstance(incoming, cls):
            return incoming
        if isinstance(incoming, basestring):
            return cls.from_rank_file(*common.square_name_to_indices(incoming))
        try:
            rank_index, file_index = incoming
        except:
            assert isinstance(incoming, int)
            return cls(incoming)
        else:
            return cls.from_rank_file(rank_index, file_index)


    @classmethod
    def src_dst_provide_position(cls, function):
        @functools.wraps(function)
        def wrapped(self, incoming_src, incoming_dst, *args, **kwargs):
            return function(self, cls.make(incoming_src),
                            cls.make(incoming_dst), *args, **kwargs)
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
            raise common.IllegalPositionError()
        return cls(rank_index * 8 + file_index)

    def __init__(self, index):
        self.index = index

    @property
    def rank_index(self):
        return (self.index & ~7) >> 3

    @property
    def file_index(self):
        return self.index & 7

    @property
    def algebraic(self):
        return (common.index_to_file(self.file_index) +
                common.index_to_rank(self.rank_index))

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

        return self.from_rank_file(self.rank_index + rank_delta,
                                   self.file_index + file_delta)

    def __repr__(self):
        return 'Position({0})'.format(self.algebraic)

    def __hash__(self):
        return hash(self.index)

    def __eq__(self, other):
        return self.index == other.index
