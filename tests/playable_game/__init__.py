import testify as T
from playable_game import common
from playable_game import board
from playable_game import notation
from playable_game import rules


def clear_everything_from_board(board):
	for square_tuple, piece in board:
		board.set_piece(*square_tuple)


class BasePlayableChessGameTestCase(T.TestCase):

	__test__ = False

	@T.let
	def chess_board(self):
		return board.BasicChessBoard()

	@T.let
	def notation_processor(self):
		return notation.ChessNotationProcessor(self.chess_board)

	@T.let
	def chess_rules(self):
		return self.notation_processor._rules

	def make_legal_move(self, *args):
		return self.chess_rules.make_legal_move(common.MoveInfo(*args))

	def make_legal_moves(self, moves):
		for move in moves:
			self.make_legal_move(*move)

	def set_piece(self, algebraic_move, piece):
		self.chess_board.set_piece(
			*notation.ChessNotationProcessor.square_name_to_indices(algebraic_move),
			piece=piece
		)


class ClearedBoardPlayableChessGameTestCase(BasePlayableChessGameTestCase):

	class ClearChessBoard(board.BasicChessBoard):

		@property
		def _new_board(self):
			return [
				[None]*4 + ['k'] + [None]*3,
				common.make_eight(None),
				common.make_eight(None),
				common.make_eight(None),
				common.make_eight(None),
				common.make_eight(None),
				common.make_eight(None),
				[None]*4 + ['K'] + [None]*3,
			]

	@T.let
	def chess_board(self):
		return self.ClearChessBoard()
