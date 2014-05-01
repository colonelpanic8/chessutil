from __future__ import absolute_import

from .position import Position
from .pieces import Piece



class Move(object):

    finalized_attributes = ('piece', 'taken_piece', 'disambiguation', 'delivers_check')

    @Position.src_dst_provide_position
    def __init__(self, source, destination, chess_rules, promotion=None):
        self.source = source
        self.destination = destination
        self.promotion = Piece.get_promotion_class(promotion)
        self.chess_rules = chess_rules

    def finalize(self):
        for attribute in self.finalized_attributes:
            self.__dict__[attribute] = getattr(self, attribute)
        self.__class__ = FinalizedMove

    @property
    def piece(self):
        return self.chess_rules[self.source]

    @property
    def taken_piece(self):
        return self.chess_rules[self.destination]

    @property
    def disambiguation(self):
        return self.piece.build_disambiguation(self.chess_rules, self)

    @property
    def delivers_check(self):
        return self.chess_rules.move_checks(self)

    @property
    def uci(self):
        return (self.source.algebraic + self.destination.algebraic +
                self.promotion.character)

    @property
    def take_string(self):
        return '' if self.taken_piece.is_empty else 'x'

    @property
    def check_string(self):
        return '+' if self.delivers_check else ''

    @property
    def promotion_string(self):
        return '' if self.promotion is None else '={0}'.format(
            self.promotion.character
        )

    @property
    def algebraic(self):
        if self.is_kingside_castle:
            return 'O-O'
        if self.is_queenside_castle:
            return 'O-O-O'
        return ''.join([self.piece.move_prefix, self.disambiguation,
                        self.take_string, self.destination.algebraic,
                        self.promotion_string, self.check_string])

    @property
    def is_kingside_castle(self):
        return (self.piece.character == 'k' and
                self.source.file_index == 4 and
                self.destination.file_index == 6)

    @property
    def is_queenside_castle(self):
        return (self.piece.character == 'k' and
                self.source.file_index == 4 and
                self.destination.file_index == 2)

    def __repr__(self):
        return "Move({0})".format(self.algebraic)

    def __eq__(self, other):
        return (type(self) == type(other) and
                self.destination == other.destination and
                self.source == other.source and
                self.chess_rules == other.chess_rules)


class FinalizedMove(Move):

    piece = taken_piece = disambiguation = delivers_check = None