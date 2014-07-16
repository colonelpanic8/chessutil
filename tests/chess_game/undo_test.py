# -*- coding: utf-8 -*-
import pytest

from chess_game import board, common, notation, pieces, rules


@pytest.fixture
def chess_board():
    return board.BasicChessBoard()

@pytest.fixture
def chess_rules(chess_board):
    return rules.ChessRules(chess_board)

@pytest.fixture
def notation_processor(chess_rules):
    return notation.ChessNotationProcessor(chess_rules)

def test_no_move_found(notation_processor):
    with pytest.raises(common.ImpossibleMoveError):
        notation_processor.parse_algebraic_move('Qcb2')

def test_one_move_undo(chess_rules, notation_processor):
    finalized_move = chess_rules.make_legal_move(notation_processor.parse_algebraic_move('e4'))
    # assert finalized_move.board_state
