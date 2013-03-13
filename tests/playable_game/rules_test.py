import testify as T

from . import clear_everything_but_kings_from_board
from playable_game import common
from playable_game import board
from playable_game import notation
from playable_game import rules


class BaseChessRulesTestCase(T.TestCase):

	__test__ = False

	@T.let
	def chess_board(self):
		return board.BasicChessBoard()

	@T.let
	def chess_rules(self):
		return rules.ChessRules(self.chess_board)

	def make_legal_move(self, *args):
		self.chess_rules.make_legal_move(common.MoveInfo(*args))

	def make_legal_moves(self, moves):
		for move in moves:
			self.make_legal_move(*move)


class ClearBoardChessRulesTestCase(BaseChessRulesTestCase):

	@T.setup
	def clear_board(self):
		clear_everything_but_kings_from_board(self.chess_board)

	def test_en_passant(self):
		self.chess_board[6][0] = 'P'
		self.chess_board[4][1] = 'p'
		self.chess_rules.action = common.BLACK
		self.make_legal_moves(
			[
				((6, 0), (4, 0)),
				((4, 1), (5, 0))
			]
		)
		T.assert_equal(
			
		)

		self.chess_board[1][6] = 'p'
		self.chess_board[3][7] = 'P'
		self.chess_rules.action = common.BLACK
		self.make_legal_move((1, 6), (3, 6))
		T.assert_sets_equal(
			set(self.chess_rules.get_legal_moves(4, 1)),
			set([(2, 7), (2, 6)])
		)


class DefaultBoardChessRulesTestCase(BaseChessRulesTestCase):

	def test_kingside_castling(self):
		moves = [
			((1, 4), (3, 4)),
			((6, 4), (4, 4)),
			((0, 6), (2, 5)),
			((7, 6), (5, 5)),
			((0, 5), (1, 4)),
			((7, 5), (6, 4)),
		]
		for move_num, move in enumerate(moves):
			self.make_legal_move(*move)
			rank = (move_num + 1) % 2 * 7
			assert (rank, 6) not in self.chess_rules.get_legal_moves(rank, 4)

		self.make_legal_move((0, 4), (0, 6))
		T.assert_equal(self.chess_board[0][6], 'k')
		T.assert_equal(self.chess_board[0][5], 'r')

		self.make_legal_move((7, 4), (7, 6))
		T.assert_equal(self.chess_board[7][6], 'K')
		T.assert_equal(self.chess_board[7][5], 'R')

	def test_get_item_of_chess_board(self):
		T.assert_equal(self.chess_board[0][0], 'r')

	def test_get_legal_moves_with_queen_and_double_check(self):
		self.chess_board[1][4] = 'q'
		self.chess_board[2][5] = 'P'
		self.chess_board[5][0] = 'b'

		all_moves = set()
		# All the straight moves.
		all_moves.update([(i, 4) for i in range (2, 7)])
		# Should be able to take the blocking pawn.
		all_moves.add((2, 5))
		# Up to the blocking bishop.
		all_moves.update([(1 + i, 4 - i) for i in range(1,4)])
		T.assert_sets_equal(
			set(self.chess_rules.get_legal_moves(1,4)),
			all_moves
		)
		self.chess_board[1][5] = None

		all_moves.add((1, 5))

		T.assert_sets_equal(
			set(self.chess_rules.get_legal_moves(1,4)),
			set(all_moves)
		)

		# The only available moves should be on the current file.
		self.chess_board[4][4] = 'R'
		T.assert_sets_equal(
			set(self.chess_rules.get_legal_moves(1,4)),
			set([(i,4) for i in range(2,5)])
		)

		# There should be no available moves because of the double check.
		self.chess_board.set_piece(1, 5, 'B')
		T.assert_sets_equal(set(self.chess_rules.get_legal_moves(1,4)), set())

		# The king has to take.
		T.assert_sets_equal(set(self.chess_rules.get_legal_moves(0,4)), set([(1,5)]))

	def test_get_legal_moves_for_rook_with_capture(self):
		self.chess_board._board[1][0] = None
		T.assert_sets_equal(
			set(self.chess_rules.get_legal_moves(0, 0)),
			set([(i, 0) for i in range (1, 7)])
		)

	def test_get_legal_moves_for_rook_without_capture(self):
		self.chess_rules.make_legal_move(common.MoveInfo((1, 0), (3, 0)))
		self.chess_rules.make_legal_move(common.MoveInfo((6, 0), (4, 0)))
		T.assert_sets_equal(
			set(self.chess_rules.get_legal_moves(0, 0)),
			set([(i, 0) for i in range (1, 3)])
		)
		T.assert_sets_equal(set(self.chess_rules.get_legal_moves(3, 0)), set())
		self.chess_rules.make_legal_move(common.MoveInfo((1, 1), (3, 1)))
		T.assert_sets_equal(set(self.chess_rules.get_legal_moves(4, 0)), set([(3, 1)]))

	def test_double_pawn_move(self):
		self.make_legal_move((1, 3), (3, 3))
		self.make_legal_move((6, 3), (4, 3))
		T.assert_equal(self.chess_board[3][3], 'p')
		T.assert_equal(self.chess_board[4][3], 'P')

		self.chess_board[3][7] = 'P'
		T.assert_raises(
			common.IllegalMoveError,
			self.make_legal_move,
			(1, 7), (3, 7)
		)

		self.chess_board[2][6] = 'p'
		T.assert_raises(
			common.IllegalMoveError,
			self.make_legal_move,
			(1, 6), (3, 6)
		)
	def test_active_color_error(self):
		T.assert_raises(
			common.ActiveColorError,
			self.chess_rules.get_legal_moves,
			7, 0
		)

		self.chess_rules.make_legal_move(common.MoveInfo((1, 0), (3, 0)))

		T.assert_raises(
			common.ActiveColorError,
			self.chess_rules.get_legal_moves,
			0, 0
		)


if __name__ == '__main__':
	T.run()
