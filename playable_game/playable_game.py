

class PlayableChessGame(object):

	def make_move_with_uci_notation(self, move):
		return self.make_move_with_square_names(move[:2], move[2:])

	def make_move_with_square_names(self, source, dest, promotion):
		return self._rules.make_legal_move(
			self.square_name_to_indices(source),
			self.square_name_to_indices(dest)
		)
