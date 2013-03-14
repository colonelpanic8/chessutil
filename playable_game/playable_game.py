from . import common
from . import notation


class PlayableChessGame(object):

	def __init__(self):
		self._notation_processor = notation.ChessNotationProcessor()
		self._board = self._notation_processor._board
		self._rules = self._notation_processor._rules

	def make_move_from_algebraic_and_return_uci(self, algebraic_move):
		move_info = self._notation_processor.parse_algebraic_move(algebraic_move)
		self._rules.make_legal_move(move_info)
		return self._notation_processor.move_info_to_uci(move_info)
