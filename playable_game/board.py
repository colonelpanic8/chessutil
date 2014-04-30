from __future__ import absolute_import

from . import common
from . import pieces
from .position import Position


class ChessBoard(object):

    def get_piece(self, position):
        raise NotImplemented()

    def set_piece(self, position, moved_piece):
        raise NotImplemented()

    def make_move(self, source, dest, moved_piece=None):
        if moved_piece is None:
            moved_piece = self.get_piece(source)
        self.set_piece(dest, piece=moved_piece)
        self.set_piece(source)

    horizontal_table_border = "  +-----------------+"

    def print_board(self):
        print self.horizontal_table_border
        for rank_index in range(8)[::-1]:
            row = [
                self[rank_index, file_index] for file_index in range(8)
            ]
            print "{0} | {1} {2} {3} {4} {5} {6} {7} {8} |".format(
                rank_index + 1,
                *map(lambda x: "." if x is None else x, row)
            )
        print self.horizontal_table_border
        print "    A B C D E F G H"

    @property
    def _new_board_array(self):
        return (
            pieces.build_back_rank(common.color.WHITE) +
            pieces.build_pawn_rank(common.color.WHITE) +
            [pieces.Empty for _ in range(32)] +
            pieces.build_pawn_rank(common.color.BLACK) +
            pieces.build_back_rank(common.color.BLACK)
        )

    def __setitem__(self, position, value):
        return self.set_piece(position, piece=value)

    def __getitem__(self, position):
        return self.get_piece(position)


class BasicChessBoard(ChessBoard):

    def __init__(self):
        self.reset_board()

    def reset_board(self):
        self._board = self._new_board_array

    @Position.provide_position
    def get_piece(self, position):
        return self._board[position.index]

    @Position.provide_position
    def set_piece(self, position, piece=pieces.Empty):
        self._board[position.index] = piece


class DeltaChessBoard(ChessBoard):

    def __init__(self, parent):
        self.parent = parent
        self.reset_to_parent()

    def reset_to_parent(self):
        self.delta_dictionary = {}

    @Position.provide_position
    def get_piece(self, position):
        piece = self.delta_dictionary.get(position, None)
        if piece is None:
            return self.parent[position]
        return piece

    @Position.provide_position
    def set_piece(self, position, piece=pieces.Empty):
        self.delta_dictionary[position] = piece
