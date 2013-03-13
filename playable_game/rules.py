from __future__ import absolute_import
import functools

from . import board
from . import common


class ChessRulesLegalMoveFunctionRegistrar(type):

	piece_to_funtion_map = {}

	def __init__(self, *args, **kwargs):
		self.piece_to_funtion_map = self.piece_to_funtion_map
		super(ChessRulesLegalMoveFunctionRegistrar, self).__init__(*args, **kwargs)

	@classmethod
	def register_legal_move_function(cls, function, piece):
		cls.piece_to_funtion_map[piece] = function
		return function

	@classmethod
	def register_for_piece(cls, piece):
		return functools.partial(
			cls.register_legal_move_function,
			piece=piece
		)


class ChessRules(object):

	__metaclass__ = ChessRulesLegalMoveFunctionRegistrar

	def __init__(self, board=None):
		if board == None:
			board = board.BasicChessBoard()
		self._board = board
		self.action = common.WHITE
		self.moves = []

	def get_legal_moves(self, rank_index, file_index):
		if self._board.get_piece_color_on_square(rank_index, file_index) != self.action:
			raise common.ActiveColorError()
		return self._filter_moves_for_king_safety(
			(rank_index, file_index),
			self._get_squares_threatened_by(rank_index, file_index)
		)

	def is_square_threatened(self, square, by_color=common.WHITE):
		for i in range(8):
			for j in range(8):
				if self._board.get_piece_color_on_square(i, j) == by_color:
					if square in set(self._get_squares_threatened_by(i, j)):
						return True
		return False

	def is_legal_move(self, source, destination):
		return destination in self.get_legal_moves(*source)

	def make_legal_move(self, move_info):
		if not self.is_legal_move(move_info.source, move_info.destination):
			raise common.IllegalMoveError()

		piece = self._board.get_piece(*move_info.source)

		# Make sure that we got promotion info if we need it, and that we didn't
		# get it if we don't.
		if piece.lower() == 'p' and move_info.destination[0] in (0, 7):
			if move_info.promotion not in ('Q', 'R', 'B', 'N'):
				raise common.IllegalMoveError("You must specify a promotion.")
			else:
				piece = move_info.promotion
				if self.action == common.WHITE:
					piece = piece.lower()
		elif move_info.promotion is not None:
			raise common.IllegalMoveError("Promotion not allowed for this move.")

		self._board.make_move(move_info.source, move_info.destination, piece)
		self.action = common.opponent_of(self.action)
		self.moves.append(move_info)

	############################################################################
	# Private Methods
	############################################################################

	def _get_legal_moves_function_for_piece(self, piece):
		return self.piece_to_funtion_map[piece.lower()]

	def _get_squares_threatened_by(self, rank_index, file_index):
		piece = self._board.get_piece(rank_index, file_index)
		return self._get_legal_moves_function_for_piece(piece)(self, rank_index, file_index)

	def _filter_moves_for_king_safety(self, start_position, moves):
		piece = self._board.get_piece(*start_position)
		piece_color = self._board.get_piece_color_on_square(*start_position)
		king_position = self._board.get_king_postion_for_color(piece_color)
		delta_board = board.DeltaChessBoard(self._board)
		delta_rules = ChessRules(delta_board)

		if piece.lower() != 'k':
			# Do an initial check to see if we can avoid checking every move.
			delta_board.set_piece(*start_position)
			if not delta_rules.is_square_threatened(
				king_position,
				by_color=common.opponent_of(piece_color)
			):
				return moves

		king_safe_moves = []
		for move in moves:
			delta_board.reset_to_parent()
			delta_board.make_move(start_position, move, piece)
			if not delta_rules.is_square_threatened(
				king_position,
				by_color=common.opponent_of(piece_color)
			):
				king_safe_moves.append(move)

		return king_safe_moves

	_diagonals = [(-1, 1), (1, -1), (1, 1), (-1, -1)]
	_straights = [(1, 0), (-1, 0), (0, 1), (0, -1)]

	def _threatened_moves_for_sliding_piece(
		self,
		rank_index,
		file_index,
		straight=False,
		diagonal=False
	):
		opponent_color = common.opponent_of(
			self._board.get_piece_color_on_square(rank_index, file_index)
		)
		directions = []
		if diagonal:
			directions.extend(self._diagonals)
		if straight:
			directions.extend(self._straights)

		threatened_moves = []
		for rank_direction, file_direction in directions:
			current_rank = rank_index + rank_direction
			current_file = file_index + file_direction
			while self._board.is_empty_square(current_rank, current_file):
				threatened_moves.append((current_rank, current_file))
				current_rank += rank_direction
				current_file += file_direction
			if self._board.is_color_piece_on_square(
				current_rank,
				current_file,
				color=opponent_color
			):
				threatened_moves.append((current_rank, current_file))

		return threatened_moves

	@ChessRulesLegalMoveFunctionRegistrar.register_for_piece('k')
	def _threatened_moves_for_king(self, rank_index, file_index):
		opponent_color = common.opponent_of(
			self._board.get_piece_color_on_square(rank_index, file_index)
		)

		threatened_moves = []
		for rank_direction, file_direction in self._diagonals + self._straights:
			move_rank = rank_index + rank_direction
			move_file = file_index + file_direction
			if self._board.is_color_or_empty_square(move_rank, move_file, color=opponent_color):
				threatened_moves.append((move_rank, move_file))
		return threatened_moves

	@ChessRulesLegalMoveFunctionRegistrar.register_for_piece('q')
	def _threatened_moves_for_queen(self, *args):
		return self._threatened_moves_for_sliding_piece(*args, straight=True, diagonal=True)

	@ChessRulesLegalMoveFunctionRegistrar.register_for_piece('r')
	def _threatened_moves_for_rook(self, *args):
		return self._threatened_moves_for_sliding_piece(*args, straight=True)

	@ChessRulesLegalMoveFunctionRegistrar.register_for_piece('b')
	def _threatened_moves_for_bishop(self, *args):
		return self._threatened_moves_for_sliding_piece(*args, diagonal=True)

	knight_deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

	@ChessRulesLegalMoveFunctionRegistrar.register_for_piece('n')
	def _threatened_moves_for_knight(self, rank_index, file_index):
		opponent_color = common.opponent_of(
			self._board.get_piece_color_on_square(rank_index, file_index)
		)

		threatened_moves = []
		for rank_delta, file_delta in self.knight_deltas:
			move_rank = rank_index + rank_delta
			move_file = file_index + file_delta
			if self._board.is_color_or_empty_square(move_rank, move_file, color=opponent_color):
				threatened_moves.append((move_rank, move_file))
		return threatened_moves

	def _check_pawn_capture_move(self, rank_index, file_index, color=common.WHITE):
		return self._board.is_color_piece_on_square(
			rank_index,
			file_index,
			color=common.opponent_of(color)
		)

	@ChessRulesLegalMoveFunctionRegistrar.register_for_piece('p')
	def _threatened_moves_for_pawn(self, rank_index, file_index):
		piece_color = self._board.get_piece_color_on_square(rank_index, file_index)
		threatened_moves = []

		check_capture_move = functools.partial(
			self._check_pawn_capture_move,
			color=piece_color
		)
		new_rank = rank_index + piece_color
		double_move_rank = 3 if piece_color is common.WHITE else 4
		moves_with_predicates = [
			((new_rank, file_index + 1), check_capture_move),
			((new_rank, file_index - 1), check_capture_move),
			((new_rank, file_index), self._board.is_empty_square),
			(
				(rank_index + (2 * piece_color), file_index),
				lambda r, f: r == double_move_rank and self._board.is_empty_square(r, f)
			)
		]
		for move_tuple, predicate in moves_with_predicates:
			if predicate(*move_tuple):
				threatened_moves.append(move_tuple)

		return threatened_moves
