import testify as T

from . import clear_everything_but_kings_from_board
from playable_game import common
from playable_game import board
from playable_game import notation


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

	def check_move_info(self, algebraic_move, *args):
		T.assert_equal(
			self.notation_processor.parse_algebraic_move(algebraic_move),
			common.MoveInfo(*args)
		)

	def set_piece(self, algebraic_move, piece):
		self.chess_board.set_piece(
			*notation.ChessNotationProcessor.square_name_to_indices(algebraic_move),
			piece=piece
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
		self.check_move_info('exd4', (4, 4) (3, 3))

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
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('O-O'),
			common.MoveInfo((0, 4), (0, 6))
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('O-O-O'),
			common.MoveInfo((0, 4), (0, 2))
		)

		self.chess_rules.action = common.BLACK
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('O-O'),
			common.MoveInfo((7, 4), (7, 6))
		)
		T.assert_equal(
			self.notation_processor.parse_algebraic_move('O-O-O'),
			common.MoveInfo((7, 4), (7, 2))
		)

	def test_rank_and_file_disambiguation(self):
		self.check_move_info('Qa4xa5', (3, 0), (4, 0))

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
