from . import common
from . import board
from . import rules


class ChessNotationProcessor(object):

	def __init__(self, chess_board=None):
		if chess_board == None:
			chess_board = board.BasicChessBoard()
		self._board = chess_board
		self._rules = rules.ChessRules(self._board)

	def parse_uci_move(self, move):
		promotion = None
		if len(move) == 5:
			promotion = move[-1].upper()
			move = move[:-1]
		assert len(move) == 4
		return self.make_move_info_from_square_names(move[:2], move[2:], promotion)

	def parse_square_names_move(self, source, dest, promotion=None):
		return common.PromotionMoveInfo(
			self.square_name_to_indices(source),
			self.square_name_to_indices(dest),
			promotion=promotion
		)

	def parse_algebraic_move(self, algebraic_move):
		algebraic_move = algebraic_move.strip(' \n+#!?')
		# Handle Castling
		if algebraic_move == "O-O":
			if self._rules.action == common.WHITE:
				return common.MoveInfo((0, 4), (0, 6))
			else:
				return common.MoveInfo((7, 4), (7, 6))

		if algebraic_move == "O-O-O":
			if self._rules.action == common.WHITE:
				return common.MoveInfo((0, 4), (0, 2))
			else:
				return common.MoveInfo((7, 4), (7, 2))

		if algebraic_move[0].islower():
			return self._parse_pawn_move(algebraic_move)
		else:
			source_file = None
			source_rank = None
			piece_type = algebraic_move[0]
			disambiguation = algebraic_move[1:-2]
			disambiguation = disambiguation.strip('x')
			destination = self.square_name_to_indices(algebraic_move[-2:])
			if disambiguation:
				length = len(disambiguation)
				if length > 2:
					raise common.InvalidNotationError()
				if length == 2:
					return common.MoveInfo(
						self.square_name_to_indices(disambiguation),
						destination
					)
				else:
					try:
						value = int(disambiguation)
					except ValueError:
						source_file = self.file_to_index(disambiguation)
					else:
						source_rank = self.rank_to_index(value)

		if self._rules.action == common.WHITE:
			piece_type = piece_type.lower()
		source = self._rules.find_piece(
			piece_type,
			destination,
			source_rank=source_rank,
			source_file=source_file
		)
		return common.MoveInfo(source, destination)

	def _parse_pawn_move(self, algebraic_move):
		# Clean up the textmove
		"".join(algebraic_move.split("e.p."))

		if '=' in algebraic_move:
			equals_position = algebraic_move.index('=')
			promotion = algebraic_move[equals_position+1]
			algebraic_move = algebraic_move[:equals_position]
		else:
			promotion = None

		destination = self.square_name_to_indices(algebraic_move[-2:])
		disambiguation = algebraic_move[:-2]
		double_move_rank = 3 if self._rules.action is common.WHITE else 4
		if disambiguation:
			source = (destination[0] - self._rules.action, self.file_to_index(disambiguation[0]))
		elif destination[0] == double_move_rank and not self._board.get_piece(
			destination[0] - self._rules.action,
			destination[1]
		):
			source = (destination[0] - 2 * self._rules.action, destination[1])
		else:
			source = (destination[0] - self._rules.action, destination[1])

		return common.PromotionMoveInfo(source, destination, promotion)

	@classmethod
	def index_to_file(cls, index):
		return chr(index + 97)

	@classmethod
	def index_to_rank(cls, index):
		return str(index + 1)

	@classmethod
	def index_tuple_to_file_rank_string(cls, rank_index, file_index):
		return cls.index_to_file(file_index) + cls.index_to_rank(rank_index)

	@classmethod
	def move_info_to_uci(cls, move_info):
		source = cls.index_tuple_to_file_rank_string(*move_info.source)
		destination = cls.index_tuple_to_file_rank_string(*move_info.destination)
		promotion = move_info.promotion if move_info.promotion else ''
		return "{0}{1}{2}".format(source, destination, promotion)

	@classmethod
	def file_to_index(cls, file_char):
		assert 'a' <= file_char <= 'h'
		return ord(file_char) - 97

	@classmethod
	def rank_to_index(cls, rank):
		assert 0 < int(rank) <= 8
		return int(rank) - 1

	@classmethod
	def square_name_to_indices(cls, square_name):
		file_char, rank_char = square_name
		return cls.rank_to_index(int(rank_char)), cls.file_to_index(file_char)
