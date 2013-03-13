import testify as T

from . import clear_everything_but_kings_from_board
from chess_board import common
from chess_board import board
from chess_board import notation


class ChessNotationProcessorTest(T.TestCase):

	@T.let
	def chess_board(self):
		return board.BasicChessBoard()

	@T.let
	def notation_processor(self):
		return notation.ChessNotationProcessor(self.chess_board)

	@T.let
	def chess_rules(self):
		return self.notation_processor._rules

	@T.setup
	def clear_board(self):
		clear_everything_but_kings_from_board(self.chess_board)

	def test_double_pawn_move(self):
		self.chess_board.set_piece(
			*self.notation_processor.square_name_to_indices('e2'),
			piece='p'
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('e4'),
			((1, 4), (3, 4))
		)
		T.assert_equal(
			self

		self.chess_board.set_piece(
			*self.notation_processor.square_name_to_indices('e3'),
			piece='p'
		)

		T.assert_equal(
			self.notation_processor.parse_algebraic_move('e4'),
			((2, 4), (3, 4))
		)

		self.chess_board.set_piece(
			*self.notation_processor.square_name_to_indices('d4'),
			piece='P'
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('exd4'),
			((2, 4), (3, 3))
		)

		self.chess_board.set_piece(
			*self.notation_processor.square_name_to_indices('f7'),
			piece='P'
		)
		self.chess_board.set_piece(
			*self.notation_processor.square_name_to_indices('e6'),
			piece='p'
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('exf7+'),
			((5, 4), (6, 5))
		)

	def test_promotion(self):
		self.chess_board.set_piece(
			*self.notation_processor.square_name_to_indices('a7'),
			piece='P'
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('a8=Q+'),
			((6, 0), (7, 0))
		)

	def test_file_disambiguation(self):
		pass

	def test_rank_disambiguation(self):
		pass

	def test_rank_and_file_disambiguation(self):
		pass

	def test_bishop_move_no_disambiguation(self):
		pass

	def test_knight_move_no_disambiguation(self):
		pass

	def test_rook_move_no_disambiguation(self):
		pass

	def test_queen_move_no_disambiguation(self):
		pass

	def test_king_move(self):
		pass


if __name__ == '__main__':
	T.run()
