import functools
from collections import namedtuple

class color(object):
    WHITE = 1
    NONE = 0
    BLACK = -1


class IllegalPositionError(Exception): pass


_bool_or_none_to_color_map = {
    True: color.WHITE,
    False: color.BLACK,
    None: color.NONE
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