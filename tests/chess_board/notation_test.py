import testify as T

from chess_board import common
from chess_board import notation


class ChessNotationProcessorTest(T.TestCase):

	@T.let
	def notation_processor(self):
		return notation.ChessNotationProcessor()

	def test_pawn_moves(self):
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('e4'),
			((1, 4), (3, 4))
		)

		self.notation_processor._board.set_peice(2, 4, peice='p')

		T.assert_equal(
			self.notation_processor.parse_algebraic_move('e4'),
			((2, 4), (3, 4))
		)

		T.assert_equal(
			self.notation_processor.parse_algebraic_move('exd4'),
			((2, 4), (3, 3))
		)

	def test_promotion(self):
		pass

	def test_file_disambiguation(self):
		pass

	def test_rank_disambiguation(self):
		pass

	def test_rank_and_file_disambiguation(self):
		pass


if __name__ == '__main__':
	T.run()
