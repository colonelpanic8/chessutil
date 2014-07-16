# -*- coding: utf-8 -*-
from . import *


class ChessNotationProcessorTest(BasePlayableChessGameTestCase):

    def test_game_start(self):
        self.make_legal_move((1, 4), (3, 4))
        self.check_move_info('e5', (6, 4), (4, 4))


class ClearedBoardChessNotationProcessorTest(ClearedBoardPlayableChessGameTestCase):

    def test_parse_long_uci_string(self):
        T.assert_equal(
            self.notation_processor.parse_long_uci_string('e4e5a6a7b3b5e7e8qd7d8rd3d4'),
            ['e4e5', 'a6a7', 'b3b5', 'e7e8q', 'd7d8r', 'd3d4']
        )

    def test_pawn_move_parsing(self):
        self.chess_rules.action = common.color.WHITE
        self.set_piece('f7', pieces.Pawn(common.color.WHITE))
        self.set_piece('e6', pieces.Pawn(common.color.WHITE))
        self.check_move_info('exf7+', (5, 4), (6, 5))
        self.check_move_info('exf7#', (5, 4), (6, 5))

        # Check double pawn move.
        self.set_piece('e2', pieces.Pawn(common.color.WHITE))
        self.check_move_info('e4', (1, 4), (3, 4))

        # Check that the right pawn is selected when there are two in a file.
        self.set_piece('e3', pieces.Pawn(common.color.WHITE))
        self.check_move_info('e4', (2, 4), (3, 4))
        self.check_move_info('exd4', (2, 4), (3, 3))

        # Check that the selected pawn is affected by the current action.
        self.chess_rules.action = common.color.BLACK
        self.set_piece('e5', pieces.Pawn(common.color.WHITE))
        self.check_move_info('e4', (4, 4), (3, 4))
        self.check_move_info('exd4', (4, 4), (3, 3))

    def test_promotion(self):
        self.set_piece('a7', pieces.Pawn(common.color.WHITE))
        T.assert_equal(
            self.notation_processor.parse_algebraic_move('a8=Q+'),
            self.build_move((6, 0), (7, 0), pieces.Queen)
        )
        T.assert_equal(
            self.notation_processor.parse_algebraic_move('a8=R'),
            self.build_move((6, 0), (7, 0), pieces.Rook)
        )

        self.chess_rules.action = common.color.BLACK
        T.assert_equal(
            self.notation_processor.parse_algebraic_move('a1=R'),
            self.build_move((1, 0), (0, 0), pieces.Rook)
        )

        T.assert_equal(
            self.notation_processor.parse_algebraic_move('bxa1=R'),
            self.build_move((1, 1), (0, 0), pieces.Rook)
        )

    def test_castling(self):
        self.chess_rules.action = common.color.WHITE
        self.check_move_info('O-O', (0, 4), (0, 6))
        self.check_move_info('O-O-O', (0, 4), (0, 2))

        self.chess_rules.action = common.color.BLACK
        self.check_move_info('O-O', (7, 4), (7, 6))
        self.check_move_info('O-O-O', (7, 4), (7, 2))

    def test_rank_and_file_disambiguation(self):
        self.check_move_info('Qa4xa5', (3, 0), (4, 0))

    def test_bishop_moves(self):
        self.chess_board[0, 5] = pieces.Bishop(common.color.WHITE)
        self.check_move_info('Bb5', (0, 5), (4, 1))

        self.chess_board[0, 5] = pieces.Empty
        self.chess_board[1, 4] = pieces.Bishop(common.color.WHITE)
        self.check_move_info('Bb5', (1, 4), (4, 1))

        self.chess_board[5, 0] = pieces.Bishop(common.color.WHITE)
        self.check_move_info('Beb5', (1, 4), (4, 1))
        self.check_move_info('Bab5', (5, 0), (4, 1))

        self.chess_board[3, 0] = pieces.Bishop(common.color.WHITE)
        self.check_move_info('Ba4b5', (3, 0), (4, 1))

    def test_knight_moves(self):
        self.set_piece('e2', pieces.Knight(common.color.WHITE))
        self.check_move_info('Ng3', (1, 4), (2, 6))
        self.check_move_info('Nf4', (1, 4), (3, 5))

        self.set_piece('e4', pieces.Knight(common.color.WHITE))
        self.check_move_info('N2g3', (1, 4), (2, 6))
        self.check_move_info('N4g3', (3, 4), (2, 6))
        self.check_move_info('Nf4', (1, 4), (3, 5))

        self.set_piece('g2', pieces.Knight(common.color.WHITE))
        self.check_move_info('Ngf4', (1, 6), (3, 5))
        self.set_piece('g2', pieces.Knight(common.color.BLACK))
        self.check_move_info('Nf4', (1, 4), (3, 5))
        self.chess_rules.action = common.color.BLACK
        self.check_move_info('Nf4', (1, 6), (3, 5))

    def test_rook_moves(self):
        self.chess_rules.action = common.color.BLACK

        self.set_piece('a4', pieces.Rook(common.color.BLACK))
        self.check_move_info('Re4', (3, 0), (3, 4))

        self.set_piece('h4', pieces.Rook(common.color.BLACK))
        self.check_move_info('Rae4', (3, 0), (3, 4))
        self.check_move_info('Rhe4', (3, 7), (3, 4))

    def test_queen_moves(self):
        self.set_piece('b4', pieces.Queen(common.color.WHITE))
        self.check_move_info('Qe4', (3, 1), (3, 4))

        self.set_piece('b1', pieces.Queen(common.color.WHITE))
        self.check_move_info('Qc2', (0, 1), (1, 2))
        self.check_move_info('Q1xe4+', (0, 1), (3, 4))

    def test_king_moves(self):
        self.chess_rules.action = common.color.WHITE
        self.check_move_info('Ke2', (0, 4), (1, 4))

        self.chess_rules.action = common.color.BLACK
        self.check_move_info('Ke7', (7, 4), (6, 4))

    def test_piece_location(self):
        #   +-----------------+
        # 8 | . . . . ♚ . . . |
        # 7 | . . . . . . . . |
        # 6 | . . . . . . . . |
        # 5 | . . . . ♕ . . . |
        # 4 | . ♕ . . . . . . |
        # 3 | . . ♕ . . . . . |
        # 2 | ♕ . . ♕ ♕ . . . |
        # 1 | . . . . ♔ . . . |
        #   +-----------------+
        #     A B C D E F G H
        self.set_piece('b4', pieces.Queen(common.color.WHITE))
        self.set_piece('a2', pieces.Queen(common.color.WHITE))
        self.set_piece('c3', pieces.Queen(common.color.WHITE))
        self.set_piece('d2', pieces.Queen(common.color.WHITE))
        self.set_piece('e5', pieces.Queen(common.color.WHITE))
        self.set_piece('e2', pieces.Queen(common.color.WHITE))
        self.check_move_info('Qbb2', 'b4', 'b2')
        self.check_move_info('Qab2', 'a2', 'b2')
        self.check_move_info('Qcb2', 'c3', 'b2')
        with T.assert_raises(common.ImpossibleMoveError):
            self.notation_processor.parse_algebraic_move('Qeb2')

        self.set_piece('c3', pieces.Empty)
        self.check_move_info('Qeb2', 'e5', 'b2')

    def test_no_move_found(self):
        with T.assert_raises(common.ImpossibleMoveError):
            self.notation_processor.parse_algebraic_move('Qcb2')

import pytest
@pytest.fixture
def chess_board():
    return board.BasicChessBoard()

class ClearChessBoard(board.BasicChessBoard):

    @property
    def _new_board_array(self):
        return [pieces.Empty]*4 + [pieces.King(common.color.WHITE)] + [pieces.Empty]*3 + [pieces.Empty]*48 + [pieces.Empty]*4 + [pieces.King(common.color.BLACK)] + [pieces.Empty]*3

@pytest.fixture
def cleared_board():
    return ClearChessBoard()

@pytest.fixture
def cleared_rules(cleared_board):
    return rules.ChessRules(cleared_board)

@pytest.fixture
def chess_rules(chess_board):
    return rules.ChessRules(chess_board)

@pytest.fixture
def notation_processor(chess_rules):
    return notation.ChessNotationProcessor(chess_rules)

def test_no_move_found(notation_processor):
    with pytest.raises(common.ImpossibleMoveError):
        notation_processor.parse_algebraic_move('Qcb2')

def test_ambiguous_move_error(chess_rules, notation_processor):
    chess_rules['c2'] = pieces.Queen(common.color.WHITE)
    chess_rules['c3'] = pieces.Queen(common.color.WHITE)
    with pytest.raises(common.AmbiguousAlgebraicMoveError):
        notation_processor.parse_algebraic_move('Qcb2')

def test_detects_checkmate(cleared_board):
    cleared_board['a7'] = pieces.Queen(common.color.WHITE)
    cleared_board['d6'] = pieces.Queen(common.color.WHITE)
    chess_rules = rules.ChessRules(cleared_board)
    assert Move('a7', 'e7', chess_rules).algebraic == 'Qae7#'


if __name__ == '__main__':
    T.run()
