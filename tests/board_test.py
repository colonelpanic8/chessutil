import testify as T

import board


class ChessBoardTestCase(T.TestCase):

	@T.let
	def chess_board(self):
		return board.ChessBoard()

	def test_get_legal_moves_for_queen(self):
		self.chess_board._board[1][4] = 'q'
		self.chess_board._board[2][5] = 'P'
		self.chess_board._board[5][0] = 'b'

		all_moves = set()
		# All the straight moves.
		all_moves.update([(i, 4) for i in range (2, 7)])
		# Should be able to take the blocking pawn.
		all_moves.add((2, 5))
		# Up to the blocking bishop.
		all_moves.update([(1 + i, 4 - i) for i in range(1,4)])
		T.assert_sets_equal(
			set(self.chess_board.get_legal_moves(1,4)),
			all_moves
		)
		self.chess_board._board[1][5] = None

		all_moves.add((1, 5))

		T.assert_sets_equal(
			set(self.chess_board.get_legal_moves(1,4)),
			set(all_moves)
		)

		self.chess_board._board[4][4] = 'R'

		T.assert_sets_equal(set(self.chess_board.get_legal_moves(1,4)), set())

	def test_get_legal_moves_for_rook_with_capture(self):
		self.chess_board._board[1][0] = None
		T.assert_sets_equal(
			set(self.chess_board.get_legal_moves(0, 0)),
			set([(i, 0) for i in range (1, 7)])
		)

	def test_get_legal_moves_for_rook_without_capture(self):
		self.chess_board._make_move((1, 0), (3, 0))
		self.chess_board.action *= -1
		T.assert_sets_equal(
			set(self.chess_board.get_legal_moves(0, 0)),
			set([(i, 0) for i in range (1, 3)])
		)

	def test_active_color_error(self):
		T.assert_raises(
			board.ActiveColorError,
			self.chess_board.get_legal_moves,
			7, 0
		)

		self.chess_board._make_move((1, 0), (3, 0))

		T.assert_raises(
			board.ActiveColorError,
			self.chess_board.get_legal_moves,
			0, 0
		)
