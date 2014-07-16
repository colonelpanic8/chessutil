from __future__ import absolute_import

from . import board
from . import common
from . import move
from . import pieces
from .position import Position


class ChessRules(object):

    def delta_rules(self):
        return type(self)(_board=board.DeltaChessBoard(self._board),
                          king_position=self.king_position.copy(),
                          queen_side_castling=self.queen_side_castling.copy(),
                          king_side_castling=self.king_side_castling.copy(),
                          action=self.action)

    def __init__(self, _board=None, king_position=None,
                 king_side_castling=None, queen_side_castling=None,
                 action=common.color.WHITE):
        if _board == None:
            _board = board.BasicChessBoard()
        self._board = _board
        self.action = action
        self.moves = []
        self.king_position = king_position or {
            common.color.WHITE: Position.make('e1'),
            common.color.BLACK: Position.make('e8')
        }
        self.king_side_castling = king_side_castling or {
            common.color.WHITE: True,
            common.color.BLACK: True
        }
        self.queen_side_castling = queen_side_castling or {
            common.color.WHITE: True,
            common.color.BLACK: True
        }

    @Position.provide_position
    def get_legal_moves(self, position):
        piece = self._board[position]
        if piece.is_empty:
            raise common.PieceNotFoundError()
        if self._board[position].color != self.action:
            raise common.ActiveColorError()
        return self._filter_moves_for_king_safety(
            position,
            self.get_squares_threatened_by(position)
        )

    @Position.provide_position
    def is_square_threatened(self, position, by_color=common.color.WHITE):
        for i in range(8):
            for j in range(8):
                if (self._board[i, j].color == by_color and
                    position in set(self.get_squares_threatened_by((i, j)))):
                    return True
        return False

    def get_all_threatened_squares(self, by_color):
        threatened_squares = set()
        for i in range(8):
            for j in range(8):
                if self[i, j].color == by_color:
                    threatened_squares = threatened_squares.union(set(self.get_squares_threatened_by((i, j))))
        return threatened_squares

    @Position.src_dst_provide_position
    def is_legal_move(self, source, destination):
        return destination in self.get_legal_moves(source)

    def make_legal_move(self, move):
        if not self.is_legal_move(move.source, move.destination):
            raise common.IllegalMoveError()
        self._check_promotion_info(move)
        return self._make_move(move.finalized())

    def _make_move(self, move):
        piece = self._board[move.source]
        if isinstance(piece, pieces.Pawn):
            self._handle_pawn_move(move)

        if isinstance(piece, pieces.King):
            self._handle_king_move(move)

        if move.source == Position.from_rank_file(0, 0):
            self.queen_side_castling[common.color.WHITE] = False
        if move.source == Position.from_rank_file(0, 7):
            self.king_side_castling[common.color.WHITE] = False
        if move.source == Position.from_rank_file(7, 0):
            self.queen_side_castling[common.color.BLACK] = False
        if move.source == Position.from_rank_file(7, 7):
            self.king_side_castling[common.color.BLACK] = False

        self._board.make_move(move.source, move.destination, piece)
        if move.promotion:
            self._board[move.destination] = move.promotion(piece.color)
        self.action = self.action.opponent
        self.moves.append(move)
        return move

    def _check_promotion_info(self, move):
        """Make sure that we got promotion info if we need it, and that we didn't
        get it if we don't."""
        piece = self._board[move.source]
        if isinstance(piece, pieces.Pawn):
            if not ((move.promotion is not None) ==
                    (move.destination.rank_index in (0, 7))):
                raise common.IllegalMoveError()
        elif move.promotion is not None:
            raise common.IllegalMoveError("Promotion not allowed for this move.")

    def _handle_pawn_move(self, move):
        # Handle enpassant
        if (move.destination.file_index != move.source.file_index and
           self._board[move.destination].is_empty):
            self._board.set_piece((move.source.rank_index,
                                   move.destination.file_index),
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

    @property
    def legal_moves_available(self):
        for i in range(8):
            for j in range(8):
                if self._board[i, j].color == self.action:
                    if self.get_legal_moves((i, j)):
                        return True
        return False

    @property
    def in_checkmate(self):
        return not self.legal_moves_available and self.is_king_threatened(self.action)

    @property
    def in_stalemate(self):
        return not self.legal_moves_available and not self.is_king_threatened(self.action)

    def is_move_checkmate(self, move):
        delta_board = board.DeltaChessBoard(self._board)
        delta_rules = ChessRules(delta_board)
        delta_rules._make_move(move)
        return delta_rules.in_checkmate

    @Position.provide_position
    def _filter_moves_for_king_safety(self, start_position, moves):
        moves = set(moves)
        piece = self[start_position]
        delta_board = board.DeltaChessBoard(self._board)
        delta_rules = ChessRules(delta_board)

        if isinstance(piece, pieces.King):
            self._filter_illegal_castling_moves(moves, piece, start_position)
        else:
            # Do an initial check to see if we can avoid checking every move.
            delta_rules[start_position] = pieces.Empty
            if not delta_rules.is_square_threatened(
                self.king_position[piece.color],
                by_color=piece.color.opponent
            ):
                return moves

        king_safe_moves = []
        for move_destination in moves:
            if isinstance(piece, pieces.King):
                king_position = move_destination
            else:
                king_position = self.king_position[piece.color]
            delta_board.reset_to_parent()
            # This is ugly, but it needs to be done to make sure that
            # a pawn removed by enpassant doesnt affect the
            # determination of whether the king is safe.
            if isinstance(piece, pieces.Pawn):
                delta_rules._handle_pawn_move(move.BaseMove(start_position, move_destination, self))
            delta_board.make_move(start_position, move_destination, piece)
            if not delta_rules.is_square_threatened(king_position,
                                                    by_color=piece.color.opponent):
                king_safe_moves.append(move_destination)

        return king_safe_moves

    def _filter_illegal_castling_moves(self, moves, piece, start_position):
        back_rank_index = 0 if piece.color is common.color.WHITE else 7
        if start_position == Position.make((back_rank_index, 4)):
            castling_square = Position.make((back_rank_index, 6))

            if castling_square in moves and any(
                self.is_square_threatened((back_rank_index, file_index),
                                          by_color=piece.color.opponent)
                for file_index in range(4, 7)
            ):
                moves.remove(castling_square)
            castling_square = Position.make((back_rank_index, 2))
            if castling_square in moves and any(
                self.is_square_threatened((back_rank_index, file_index),
                                          by_color=piece.color.opponent)
                    for file_index in range(2, 5)
            ):
                moves.remove(castling_square)

    @Position.provide_position
    def get_squares_threatened_by(self, position):
        return self[position].get_all_threatened_moves(position, self)

    @Position.provide_position
    def __getitem__(self, item):
        return self._board[item]

    @Position.provide_position
    def __setitem__(self, position, piece):
        if isinstance(piece, pieces.King):
            self.king_position[piece.color] = position
        self._board[position] = piece

    def can_castle_kingside(self, color):
        return self.king_side_castling[color]

    def can_castle_queenside(self, color):
        return self.queen_side_castling[color]

    def is_king_threatened(self, color):
        return self.is_square_threatened(self.king_position[color],
                                         by_color=color.opponent)

    def delivers_check(self, move):
        delta_rules = self.delta_rules()
        delta_rules._make_move(move)
        return delta_rules.is_king_threatened(delta_rules.action)
