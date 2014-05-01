from __future__ import absolute_import

from . import common
from . import pieces
from . import rules
from .move import Move
from .position import Position


class ChessNotationProcessor(object):

    def __init__(self, chess_rules=None):
        if chess_rules is None:
            self._rules = rules.ChessRules(self._board)
        else:
            self._rules = chess_rules

    def parse_uci_move(self, move):
        promotion = None
        if len(move) == 5:
            promotion = move[-1].upper()
            move = move[:-1]
        assert len(move) == 4
        return self.make_move_info_from_square_names(move[:2], move[2:], promotion)

    def parse_algebraic_move(self, algebraic_move):
        algebraic_move = algebraic_move.strip(' \n+#!?')
        if algebraic_move[0] == 'O':
            return self._parse_castle_move(algebraic_move)
        if self._is_pawn_move(algebraic_move):
            return self._parse_pawn_move(algebraic_move)

        source_file = None
        source_rank = None
        piece_string = algebraic_move[0]
        disambiguation = algebraic_move[1:-2]
        disambiguation = disambiguation.strip('x')
        destination = Position.make(algebraic_move[-2:])

        if disambiguation:
            length = len(disambiguation)
            if length > 2:
                raise common.InvalidNotationError()
            if length == 2:
                return self._build_move(Position.make(disambiguation),
                                       destination)
            else:
                try:
                    value = int(disambiguation)
                except ValueError:
                    source_file = common.file_to_index(disambiguation)
                else:
                    source_rank = common.rank_to_index(value)

        results = self._rules.find_piece(
            pieces.Piece.get_piece_class(piece_string.lower()),
            destination,
            color=self._rules.action,
            source_rank=source_rank,
            source_file=source_file,
            find_all=True
        )
        if len(results) > 1:
            print results
            raise common.AmbiguousAlgebraicMoveError()
        source, = results
        return self._build_move(source, destination)

    def _build_move(self, source, destination, promotion=None):
        return Move(source, destination, self._rules, promotion=promotion)

    def _is_pawn_move(self, algebraic_move):
        return algebraic_move[0].islower()


    def _parse_castle_move(self, algebraic_move):
        # Handle Castling
        if algebraic_move == "O-O":
            if self._rules.action == common.color.WHITE:
                return self._build_move((0, 4), (0, 6))
            else:
                return self._build_move((7, 4), (7, 6))

        if algebraic_move == "O-O-O":
            if self._rules.action == common.color.WHITE:
                return self._build_move((0, 4), (0, 2))
            else:
                return self._build_move((7, 4), (7, 2))


    def _parse_pawn_move(self, algebraic_move):
        # Clean up the textmove
        "".join(algebraic_move.split("e.p."))

        if '=' in algebraic_move:
            equals_position = algebraic_move.find('=')
            promotion = algebraic_move[equals_position + 1]
            algebraic_move = algebraic_move[:equals_position]
        else:
            promotion = None

        destination = Position.make(algebraic_move[-2:])
        disambiguation = algebraic_move[:-2]
        double_move_rank = 3 if self._rules.action is common.color.WHITE else 4
        if disambiguation:
            source = Position.make((destination.rank_index - self._rules.action,
                                   common.file_to_index(disambiguation[0])))
        elif destination.rank_index == double_move_rank and self._rules[
            destination.rank_index - self._rules.action,
            destination.file_index
        ].is_empty:
            source = Position.make((destination.rank_index - 2 * self._rules.action,
                                   destination.file_index))
        else:
            source = Position.make((destination.rank_index - self._rules.action,
                                   destination.file_index))

        return self._build_move(source, destination, promotion)