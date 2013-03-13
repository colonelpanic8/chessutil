import testify as T

import board
import notation


class NotationProcessorTestCase(T.TestCase):

	@T.let
	def notation_processor(self):
		return notation.NotationProcessor()

	@T.let
	def board(self):
		return board.ChessBoard()

	def test_parse_algebraic_move(self):
		T.assert_equal(
			notation_processor.parse_algebraic_move(self.board, 'e4')


if __name__ == '__main__':
	T.run()
