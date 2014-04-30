from __future__ import absolute_import
import functools

from . import board
from . import common
from . import pieces
from .position import Position


class ChessRules(object):

    def __init__(self, board=None):
        if board == None:
            board = board.BasicChessBoard()
        self._board = board
        self.action = common.color.WHITE
        self.moves = []
        self.king_position = {
            common.color.WHITE: Position(0, 4),
            common.color.BLACK: Position(7, 4)
        }
        self.king_side_castling = {
            common.color.WHITE: True,
            common.color.BLACK: True
        }
        self.queen_side_castling = self.king_side_castling.copy()

    @Position.provide_position
    def get_legal_moves(self, position):
        if self._board[position].color != self.action:
            raise common.ActiveColorError()
        return self._filter_moves_for_king_safety(
            position,
            self._get_squares_threatened_by(position)
        )

    @Position.provide_position
    def is_square_threatened(self, position, by_color=common.color.WHITE):
        for i in range(8):
            for j in range(8):
                if (self._board[i, j].color == by_color and
                    position in set(self._get_squares_threatened_by((i, j)))):
                    return True
        return False

    def get_all_threatened_squares(self, position, by_color):
        threatened_squares = set()
        for i in range(8):
            for j in range(8):
                if self[position].color == by_color:
                    threatened_squares.extend(self._get_squares_threatened_by((i, j)))
        return threatened_squares

    @Position.src_dst_provide_position
    def is_legal_move(self, source, destination):
        return destination in self.get_legal_moves(source)

    def make_legal_move(self, move):
        if not self.is_legal_move(move.source, move.destination):
            raise common.IllegalMoveError()

        piece = self._board.get_piece(move.source)

        # Make sure that we got promotion info if we need it, and that we didn't
        # get it if we don't.
        if isinstance(piece, pieces.Pawn):
            self._handle_pawn_move(move)
        elif move.promotion is not None:
            raise common.IllegalMoveError("Promotion not allowed for this move.")

        if isinstance(piece, pieces.King):
            self._handle_king_move(move)

        if isinstance(piece, pieces.Pawn):
            self._handle_pawn_move(move)

        if move.source == Position(0, 0):
            self.queen_side_castling[common.color.WHITE] = False
        if move.source == Position(0, 7):
            self.king_side_castling[common.color.WHITE] = False
        if move.source == Position(7, 0):
            self.queen_side_castling[common.color.BLACK] = False
        if move.source == Position(7, 7):
            self.king_side_castling[common.color.BLACK] = False

        self._board.make_move(move.source, move.destination, piece)
        self.action = self.action.opponent
        self.moves.append(move)

    def _handle_pawn_move(self, move):
        assert move.promotion is not None == move.destination.rank_index in (0, 7)

        # Handle enpassant
        if (move.destination.file_index != move.source.file_index and
           self._board[move.destination].is_empty):
            self._board.set_piece(move.source.rank_index,
                                  move.destination.file_index,
                                  pieces.Empty)

    def _handle_king_move(self, move):
        if move.is_kingside_castle:
            # Kingside castle.
            self._board.make_move((move.source.rank_index, 7),
                                  (move.source.rank_index, 5))
        if move.is_queenside_castle:
            self._board.make_move((move.source.rank_index, 0),
                                  (move.source.rank_index, 3))
        # Disable castling after a king move no matter what.
        self.king_side_castling[self.action] = False
        self.queen_side_castling[self.action] = False
        self.king_position[self.action] = move.destination

    def find_piece(self, piece_class, destination, *args, **kwargs):
        return piece_class.find(destination, self, *args, **kwargs)

    def _filter_moves_for_king_safety(self, start_position, moves):
        moves = set(moves)
        piece = self[start_position]
        delta_board = board.DeltaChessBoard(self._board)
        delta_rules = ChessRules(delta_board)

        if isinstance(piece, pieces.King):
            back_rank_index = 0 if piece.color is common.color.WHITE else 7
            if start_position == Position(back_rank_index, 4):
                castling_square = Position(back_rank_index, 6)
                if castling_square in moves and any(
                    self.is_square_threatened((back_rank_index, file_index),
                                              by_color=piece.color.opponent)
                    for file_index in range(4, 7)
                ):
                    moves.remove(castling_square)
                castling_square = (back_rank_index, 2)
                if castling_square in moves and any(
                    self.is_square_threatened(
                        (back_rank_index, file_index),
                        by_color=piece.color
                    ) for file_index in range(2, 5)
                ):
                    moves.remove(castling_square)
        else:
            # Do an initial check to see if we can avoid checking every move.
            delta_board.set_piece(start_position)
            if not delta_rules.is_square_threatened(
                delta_rules.get_king_postion_for_color(piece_color),
                by_color=common.opponent_of(piece_color)
            ):
                return moves

        king_safe_moves = []
        for move in moves:
            delta_board.reset_to_parent()
            delta_board.make_move(start_position, move, piece)
            if not delta_rules.is_square_threatened(
                delta_board.get_king_postion_for_color(piece_color),
                by_color=common.opponent_of(piece_color)
            ):
                king_safe_moves.append(move)

        return king_safe_moves

    @Position.provide_position
    def get_squares_threatened_by(self, position):
        return self[position].get_all_threatened_moves(position, self)