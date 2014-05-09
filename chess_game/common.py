from __future__ import absolute_import
import functools


class Color(int):

    @property
    def opponent(self):
        return Color(self * -1)


class color(object):

    WHITE = Color(1)
    NONE = Color(0)
    BLACK = Color(-1)


class ActiveColorError(Exception): pass
class AmbiguousAlgebraicMoveError(Exception): pass
class IllegalMoveError(Exception): pass
class IllegalPositionError(Exception): pass
class IllegalSquareError(Exception): pass
class ImpossibleMoveError(Exception): pass
class InvalidNotationError(Exception): pass
class PieceNotFoundError(Exception): pass


def listify(function):
    @functools.wraps(function)
    def wrapped(*args, **kwargs):
        return list(function(*args, **kwargs))
    return wrapped


def index_to_file(index):
    return chr(index + 97)


def index_to_rank(index):
    return str(index + 1)


def file_to_index(file_char):
    assert 'a' <= file_char <= 'h'
    return ord(file_char) - 97


def rank_to_index(rank):
    assert 0 < int(rank) <= 8
    return int(rank) - 1


def square_name_to_indices(square_name):
    file_char, rank_char = square_name
    return rank_to_index(int(rank_char)), file_to_index(file_char)


def get_piece_character(piece, use_unicode_characters=False):
    return piece.unicode_string if use_unicode_characters else str(piece)