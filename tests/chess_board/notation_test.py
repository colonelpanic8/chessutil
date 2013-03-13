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

	@T.setup
	def clear_board(self):
		clear_everything_but_kings_from_board(self.chess_board)

	def test_double_pawn_move(self):
		self.chess_board.set_peice(
			*self.notation_processor.square_name_to_indices('e2'),
			peice='p'
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('e4'),
			((1, 4), (3, 4))
		)

		self.chess_board.set_peice(
			*self.notation_processor.square_name_to_indices('e3'),
			peice='p'
		)

		T.assert_equal(
			self.notation_processor.parse_algebraic_move('e4'),
			((2, 4), (3, 4))
		)

		self.chess_board.set_peice(
			*self.notation_processor.square_name_to_indices('d4'),
			peice='P'
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('exd4'),
			((2, 4), (3, 3))
		)

	def test_promotion(self):
		self.chess_board.set_peice(
			*self.notation_processor.square_name_to_indices('a7'),
			peice='P'
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
