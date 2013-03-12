from __future__ import absolute_import
import functools
import inspect

import util


class IllegalSquareError(Exception):
	pass


class ActiveColorError(Exception):
	pass


class ChessBoardLegalMoveFunctionRegistrar(type):

	def __init__(self, *args, **kwargs):
		self.peice_to_funtion_name_map = {}
		for attr_name, attr in inspect.getmembers(self):
			peice = getattr(attr, 'peice_to_register_for', False)
			if peice:
				assert peice not in self.peice_to_funtion_name_map
				self.peice_to_funtion_name_map[peice] = attr_name
		super(ChessBoardLegalMoveFunctionRegistrar, self).__init__(*args, **kwargs)

	@classmethod
	def register_legal_move_function(cls, function, peice):
		function.peice_to_register_for = peice
		return function

	@classmethod
	def register_for_peice(cls, peice):
		return functools.partial(
			cls.register_legal_move_function,
			peice=peice
		)


class ChessBoard(object):

	__metaclass__ = ChessBoardLegalMoveFunctionRegistrar

	WHITE = 1
	NONE = 0
	BLACK = -1

	_bool_or_none_to_color_map = {
		True: WHITE,
		False: BLACK,
		None: NONE
	}

	def __init__(self):
		self.reset_board()

	############################################################################
	# Public Methods
	############################################################################

	def reset_board(self):
		self._board = self._new_board
		self.action = self.WHITE

	def get_peice(self, rank_index, file_index):
		return self._board[rank_index][file_index]

	def get_peice_color(self, peice):
		return self._bool_or_none_to_color_map[self._is_peice_white(peice)]

	def get_legal_moves(self, rank_index, file_index):
		peice = self.get_peice(rank_index, file_index)
		if self.get_peice_color(peice) != self.action:
			raise ActiveColorError()
		return self._get_legal_moves_function_for_peice(peice)(rank_index, file_index)

	def make_move_with_uci_notation(self, move):
		return self.make_move_with_square_names(move[:2], move[2:])

	def make_move_with_square_names(self, source, dest):
		return self.make_move_with_tuples(
			util.square_name_to_indices(source),
			util.square_name_to_indices(dest)
		)

	def make_move_with_tuples(self, source, dest):
		self._board[s]

	def is_peice_on_square_white(self, rank_index, file_index):
		if not self._is_legal_square(rank_index, file_index):
			raise IllegalSquareError()
		return self._is_peice_white(self._board[rank_index][file_index])

	def get_peice_color_on_square(self, rank_index, file_index):
		return self._bool_or_none_to_color_map[
			self.is_peice_on_square_white(rank_index, file_index)
		]

	############################################################################
	# Private Functions
	############################################################################

	def _is_opponents_peice_on_square(self, rank_index, file_index):
		return self._is_legal_square(rank_index, file_index) and \
			self.get_peice_color_on_square(rank_index, file_index) == self.action*-1

	def _is_empty_square(self, rank_index, file_index):
		return self._is_legal_square(rank_index, file_index) and \
			self.get_peice_color_on_square(rank_index, file_index) == self.NONE

	def _get_legal_moves_function_for_peice(self, peice):
		return getattr(self, self.peice_to_funtion_name_map[peice.lower()])

	def _is_peice_white(self, peice):
		if peice:
			return peice.islower()
		else:
			return None

	def _is_legal_square(self, rank_index, file_index):
		return 0 <= rank_index < 8 and 0 <= file_index < 8

	def _set_peice(self, rank_index, file_index, peice=None):
		self._board[rank_index][file_index] = peice

	def _make_move(self, source, dest):
		self._set_peice(*dest, peice=self.get_peice(*source))
		self._set_peice(*source)
		self.action *= -1

	@property
	def _new_board(self):
		return [
			['r','n','b','q','k','b','n','r'],
			util.make_eight('p'),
			util.make_eight(None),
			util.make_eight(None),
			util.make_eight(None),
			util.make_eight(None),
			util.make_eight('P'),
			['R','N','B','Q','K','B','N','R']
		]

	############################################################################
	# Legal Move Functions
	############################################################################

	def _check_king_safety_for_move(self):
		pass

	_diagonals = [(-1, 1), (1, -1), (1, 1), (-1, -1)]
	_straights = [(1, 0), (-1, 0), (0, 1), (0, -1)]

	def _legal_moves_for_sliding_peice(
		self,
		rank_index,
		file_index,
		straight=False,
		diagonal=False
	):
		directions = []
		if diagonal:
			directions.extend(self._diagonals)
		if straight:
			directions.extend(self._straights)

		legal_moves = []
		for rank_direction, file_direction in directions:
			current_rank = rank_index + rank_direction
			current_file = file_index + file_direction
			while self._is_empty_square(current_rank, current_file):
				legal_moves.append((current_rank, current_file))
				current_rank += rank_direction
				current_file += file_direction
			if self._is_opponents_peice_on_square(current_rank, current_file):
				legal_moves.append((current_rank, current_file))

		return legal_moves

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('q')
	def _legal_moves_for_queen(self, *args):
		return self._legal_moves_for_sliding_peice(*args, straight=True, diagonal=True)

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('r')
	def _legal_moves_for_rook(self, *args):
		return self._legal_moves_for_sliding_peice(*args, straight=True)

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('b')
	def _legal_moves_for_bishop(self, *args):
		return self._legal_moves_for_sliding_peice(*args, diagonal=True)

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('p')
	def _legal_moves_for_pawn(self, rank_index, file_index):
		legal_moves = []

		moves_with_needed_opponent_check = [
			((rank_index + 1, file_index + 1), True),
			((rank_index + 1, file_index - 1), True),
			((rank_index + 1, file_index), False)
		]
		for move_tuple, needs_opponent_in_square in moves_with_needed_opponent_check:
			if self._is_legal_square(*move_tuple) and \
				self._is_opponents_peice_on_square(*move_tuple) == needs_opponent_in_square:
				legal_moves.append(move_tuple)
