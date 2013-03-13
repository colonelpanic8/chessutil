from __future__ import absolute_import
import functools

from . import board
from . import common


class ChessRulesLegalMoveFunctionRegistrar(type):

	peice_to_funtion_map = {}

	def __init__(self, *args, **kwargs):
		self.peice_to_funtion_map = self.peice_to_funtion_map
		super(ChessRulesLegalMoveFunctionRegistrar, self).__init__(*args, **kwargs)

	@classmethod
	def register_legal_move_function(cls, function, peice):
		cls.peice_to_funtion_map[peice] = function
		return function

	@classmethod
	def register_for_peice(cls, peice):
		return functools.partial(
			cls.register_legal_move_function,
			peice=peice
		)

class ChessRules(object):

	__metaclass__ = ChessRulesLegalMoveFunctionRegistrar

	def __init__(self, board=None):
		if board == None:
			board = board.BasicChessBoard()
		self._board = board

	def get_legal_moves(self, rank_index, file_index):
		if self._board.get_peice_color_on_square(rank_index, file_index) != self._board.action:
			raise ActiveColorError()
		return self._filter_moves_for_king_safety(
			(rank_index, file_index),
			self._get_squares_threatened_by(rank_index, file_index)
		)

	def is_square_threatened(self, square, by_color=common.WHITE):
		for i in range(8):
			for j in range(8):
				if self._board.get_peice_color_on_square(i, j) == by_color:
					if square in set(self._get_squares_threatened_by(i, j)):
						return True
		return False

	############################################################################
	# Private Methods
	############################################################################

	def _get_legal_moves_function_for_peice(self, peice):
		return self.peice_to_funtion_map[peice.lower()]

	def _get_squares_threatened_by(self, rank_index, file_index):
		peice = self._board.get_peice(rank_index, file_index)
		return self._get_legal_moves_function_for_peice(peice)(self, rank_index, file_index)

	def _filter_moves_for_king_safety(self, start_position, moves):
		peice = self._board.get_peice(*start_position)
		peice_color = self._board.get_peice_color_on_square(*start_position)
		king_position = self._board.get_king_postion_for_color(peice_color)
		delta_board = chess_board.DeltaChessBoard(self._board)
		delta_rules = ChessRules(delta_board)

		if peice.lower() != 'k':
			# Do an initial check to see if we can avoid checking every move.
			delta_board.set_peice(*start_position)
			if not delta_rules.is_square_threatened(
				king_position,
				by_color=common.opponent_of(peice_color)
			):
				return moves

		king_safe_moves = []
		for move in moves:
			delta_board.reset_to_parent()
			delta_board.make_move(start_position, move)
			if not delta_rules.is_square_threatened(
				king_position,
				by_color=common.opponent_of(peice_color)
			):
				king_safe_moves.append(move)

		return king_safe_moves

	_diagonals = [(-1, 1), (1, -1), (1, 1), (-1, -1)]
	_straights = [(1, 0), (-1, 0), (0, 1), (0, -1)]

	def _threatened_moves_for_sliding_peice(
		self,
		rank_index,
		file_index,
		straight=False,
		diagonal=False
	):
		opponent_color = common.opponent_of(
			self._board.get_peice_color_on_square(rank_index, file_index)
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
			if self._board.is_color_peice_on_square(current_rank, current_file, color=opponent_color):
				threatened_moves.append((current_rank, current_file))

		return threatened_moves

	@ChessRulesLegalMoveFunctionRegistrar.register_for_peice('k')
	def _threatened_moves_for_king(self, rank_index, file_index):
		opponent_color = common.opponent_of(
			self._board.get_peice_color_on_square(rank_index, file_index)
		)

		threatened_moves = []
		for rank_direction, file_direction in self._diagonals + self._straights:
			move_rank = rank_index + rank_direction
			move_file = file_index + file_direction
			if self._board.is_color_or_empty_square(move_rank, move_file, color=opponent_color):
				threatened_moves.append((move_rank, move_file))
		return threatened_moves

	@ChessRulesLegalMoveFunctionRegistrar.register_for_peice('q')
	def _threatened_moves_for_queen(self, *args):
		return self._threatened_moves_for_sliding_peice(*args, straight=True, diagonal=True)

	@ChessRulesLegalMoveFunctionRegistrar.register_for_peice('r')
	def _threatened_moves_for_rook(self, *args):
		return self._threatened_moves_for_sliding_peice(*args, straight=True)

	@ChessRulesLegalMoveFunctionRegistrar.register_for_peice('b')
	def _threatened_moves_for_bishop(self, *args):
		return self._threatened_moves_for_sliding_peice(*args, diagonal=True)

	knight_deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

	@ChessRulesLegalMoveFunctionRegistrar.register_for_peice('n')
	def _threatened_moves_for_knight(self, rank_index, file_index):
		opponent_color = common.opponent_of(
			self._board.get_peice_color_on_square(rank_index, file_index)
		)

		threatened_moves = []
		for rank_delta, file_delta in self.knight_deltas:
			move_rank = rank_index + rank_delta
			move_file = file_index + file_delta
			if self._board.is_color_or_empty_square(move_rank, move_file, color=opponent_color):
				threatened_moves.append((move_rank, move_file))
		return threatened_moves

	def _check_pawn_capture_move(self, rank_index, file_index, opponent_color=common.WHITE):
		return self._board.is_color_peice_on_square(rank_index, file_index, color=opponent_color)

	@ChessRulesLegalMoveFunctionRegistrar.register_for_peice('p')
	def _threatened_moves_for_pawn(self, rank_index, file_index):
		opponent_color = common.opponent_of(
			self._board.get_peice_color_on_square(rank_index, file_index)
		)
		threatened_moves = []

		check_capture_move = functools.partial(
			self._check_pawn_capture_move,
			opponent_color=opponent_color
		)
		moves_with_predicates = [
			((rank_index + 1, file_index + 1), check_capture_move),
			((rank_index + 1, file_index - 1), check_capture_move),
			((rank_index + 1, file_index), self._board.is_empty_square),
			((rank_index + 2, file_index), lambda r, f: r == 3 and self._board.is_empty_square(r, f))
		]
		for move_tuple, predicate in moves_with_predicates:
			if predicate(*move_tuple):
				threatened_moves.append(move_tuple)

		return threatened_moves
