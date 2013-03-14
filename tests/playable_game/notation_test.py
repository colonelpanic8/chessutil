from . import *


class ChessNotationProcessorTest(ClearedBoardPlayableChessGameTestCase):

	def check_move_info(self, algebraic_move, *args):
		T.assert_equal(
			self.notation_processor.parse_algebraic_move(algebraic_move),
			common.MoveInfo(*args)
		)

	def test_pawn_move_parsing(self):
		self.chess_rules.action = common.WHITE
		self.set_piece('f7', 'P')
		self.set_piece('e6', 'p')
		self.check_move_info('exf7+', (5, 4), (6, 5))
		self.check_move_info('exf7#', (5, 4), (6, 5))

		# Check double pawn move.
		self.set_piece('e2', 'p')
		self.check_move_info('e4', (1, 4), (3, 4))

		# Check that the right pawn is selected when there are two in a file.
		self.set_piece('e3', 'p')
		self.check_move_info('e4', (2, 4), (3, 4))
		self.check_move_info('exd4', (2, 4), (3, 3))

		# Check that the selected pawn is affected by the current action.
		self.chess_rules.action = common.BLACK
		self.set_piece('e5', 'P')
		self.check_move_info('e4', (4, 4), (3, 4))
		self.check_move_info('exd4', (4, 4), (3, 3))

	def test_promotion(self):
		self.set_piece('a7', 'P')
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('a8=Q+'),
			common.PromotionMoveInfo((6, 0), (7, 0), 'Q')
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('a8=R'),
			common.PromotionMoveInfo((6, 0), (7, 0), 'R')
		)

		self.chess_rules.action = common.BLACK
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('a1=R'),
			common.PromotionMoveInfo((1, 0), (0, 0), 'R')
		)

		T.assert_equal(
			self.notation_processor.parse_algebraic_move('bxa1=R'),
			common.PromotionMoveInfo((1, 1), (0, 0), 'R')
		)

	def test_castling(self):
		self.chess_rules.action = common.WHITE
		self.check_move_info('O-O', (0, 4), (0, 6))
		self.check_move_info('O-O-O', (0, 4), (0, 2))

		self.chess_rules.action = common.BLACK
		self.check_move_info('O-O', (7, 4), (7, 6))
		self.check_move_info('O-O-O', (7, 4), (7, 2))

	def test_rank_and_file_disambiguation(self):
		self.check_move_info('Qa4xa5', (3, 0), (4, 0))

	def test_bishop_moves(self):
		self.chess_board[0][5] = 'b'
		self.check_move_info('Bb5', (0, 5), (1, 4))

		self.chess_board[0][5] = None
		self.chess_board[1][4] = 'b'
		self.check_move_info('Bb5', (1, 4), (1, 4))

		self.chess_board[0][5] = 'b'
		self.check_move_info('Beb5', (1, 4), (1, 4))
		self.check_move_info('Bab5', (5, 0), (1, 4))

		self.chess_board[5][0] = 'b'
		self.check_move_info('Beb5', (1, 4), (1, 4))
		self.check_move_info('Bab5', (5, 0), (1, 4))

		self.chess_board[3][0] = 'b'
		self.check_move_info('Ba4b5', (3, 0) (1, 4))

	def test_knight_moves(self):
		self.set_piece('e2', 'n')
		self.check_move_info('Ng3', (1, 4), (2, 6))
		self.check_move_info('Nf4', (1, 4), (2, 5))

		self.set_piece('e2', 'n')
		self.check_move_info('N1g3', (1, 4), (2, 6))
		self.check_move_info('N3g3', (1, 4), (2, 6))
		self.check_move_info('Nf4', (1, 4), (2, 5))

		self.set_piece('g2', 'n')
		self.check_move_info('Ngf4', (1, 6), (2, 5))
		self.set_piece('g2', 'N')
		self.check_move_info('Nf4', (1, 4), (2, 5))

		self.chess_rules.action = common.BLACK
		self.check_move_info('Nf4', (1, 6), (2, 5))

	def test_rook_moves(self):
		self.chess_rules.action = common.BLACK

		self.set_piece('a4', 'R')
		self.check_move_info('Re4', (0, 3), (4, 3))

		self.set_piece('h4', 'R')
		self.check_move_info('Rae4', (0, 3), (4, 3))
		self.check_move_info('Rhe4', (7, 3), (4, 3))

	def test_queen_moves(self):
		pass

	def test_king_moves(self):
		self.chess_rules.action = common.WHITE
		self.check_move_info('Ke2', (0, 4), (1, 4))

		self.chess_rules.action = common.BLACK
		self.check_move_info('Ke7', (7, 4), (6, 4))


if __name__ == '__main__':
	T.run()
