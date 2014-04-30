from __future__ import absolute_import

from . import common
from .pieces import Piece


class Move(object):

    @common.Position.src_dst_provide_position
    def __init__(self, source, destination, chess_board, promotion=None):
        self.source = source
        self.destination = destination
        self.promotion = Piece.get_promotion_class(promotion)
        self.piece = chess_board[source]
        self.taken_piece = chess_board[destination]
        self.disambiguation = self.piece.build_disambiguation(chess_board, self)
        self.delivers_check = chess_board.move_checks(self)

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
        if self.piece.character == 'k' and self.source.file_index == 4:
            if self.dest.file_index == 6:
                return 'O-O'
    @property
    def is_queenside_castle(self):
        if self.piece.character == 'k' and self.source.file_index == 4:
            if self.dest.file_index == 2:
                return 'O-O-O'