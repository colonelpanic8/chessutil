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

	############################################################################
	# Mandatory Override Methods
	############################################################################

	def get_peice(self, rank_index, file_index):
		raise NotImplemented()

	def set_peice(self, rank_index, file_index, peice=None):
		if peice == 'k':
			self.white_king_position = (rank_index, file_index)
		elif peice == 'K':
			self.black_king_position = (rank_index, file_index)

	############################################################################
	# Public Methods
	############################################################################

	def get_peice_color(self, peice):
		return self._bool_or_none_to_color_map[self._is_peice_white(peice)]

	def get_legal_moves(self, rank_index, file_index):
		if self.get_peice_color_on_square(rank_index, file_index) != self.action:
			raise ActiveColorError()
		return self._filter_moves_for_king_safety(
			(rank_index, file_index),
			self._get_squares_threatened_by(rank_index, file_index)
		)

	def make_move_with_uci_notation(self, move):
		return self.make_move_with_square_names(move[:2], move[2:])

	def make_move_with_square_names(self, source, dest):
		return self.make_move(
			util.square_name_to_indices(source),
			util.square_name_to_indices(dest)
		)

	def make_move(self, source, dest):
		self.set_peice(*dest, peice=self.get_peice(*source))
		self.set_peice(*source)
		self.action = self._opponent_of(self.action)
		return self

	def is_peice_on_square_white(self, rank_index, file_index):
		if not self._is_legal_square(rank_index, file_index):
			raise IllegalSquareError()
		return self._is_peice_white(self.get_peice(rank_index, file_index))

	def is_square_threatened(self, square, by_color=WHITE):
		for i in range(8):
			for j in range(8):
				if self.get_peice_color_on_square(i, j) == by_color:
					if square in set(self._get_squares_threatened_by(i, j)):
						return True
		return False

	def get_peice_color_on_square(self, rank_index, file_index):
		return self._bool_or_none_to_color_map[
			self.is_peice_on_square_white(rank_index, file_index)
		]

	horizontal_table_border = "  +-----------------+"

	def print_board(self):
		print self.horizontal_table_border
		for rank_index in range(8)[::-1]:
			row = [
				self.get_peice(rank_index, file_index) for file_index in range(8)
			]
			print "{0} | {1} {2} {3} {4} {5} {6} {7} {8} |".format(
				rank_index,
				*map(lambda x: "." if x is None else x, row)
			)
		print self.horizontal_table_border
		print "    A B C D E F G H"


	############################################################################
	# Private Methods
	############################################################################

	def _opponent_of(self, color):
		return color * -1

	def _is_color_or_empty_square(self, rank_index, file_index, color=WHITE):
		return self._is_color_peice_on_square(rank_index, file_index, color=color) or self._is_empty_square(rank_index, file_index)

	def _is_color_peice_on_square(self, rank_index, file_index, color=WHITE):
		return self._is_legal_square(rank_index, file_index) and \
			self.get_peice_color_on_square(rank_index, file_index) == color

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

	def _get_squares_threatened_by(self, rank_index, file_index):
		peice = self.get_peice(rank_index, file_index)
		return self._get_legal_moves_function_for_peice(peice)(rank_index, file_index)

	def _get_king_postion_for_color(self, color=WHITE):
		if color == self.WHITE:
			return self.white_king_position
		if color == self.BLACK:
			return self.black_king_position

	def _filter_moves_for_king_safety(self, start_position, moves):
		peice = self.get_peice(*start_position)
		peice_color = self.get_peice_color_on_square(*start_position)
		king_position = self._get_king_postion_for_color(peice_color)
		delta_board = DeltaChessBoard(self)

		if peice.lower() != 'k':
			# Do an initial check to see if we can avoid checking every move.
			delta_board.set_peice(*start_position)
			if not delta_board.is_square_threatened(
				king_position,
				by_color=self._opponent_of(peice_color)
			):
				return moves

		king_safe_moves = []
		for move in moves:
			delta_board.reset_to_parent()
			delta_board.make_move(start_position, move)
			if not delta_board.is_square_threatened(
				king_position,
				by_color=self._opponent_of(peice_color)
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
		opponent_color = self._opponent_of(
			self.get_peice_color_on_square(rank_index, file_index)
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
			while self._is_empty_square(current_rank, current_file):
				threatened_moves.append((current_rank, current_file))
				current_rank += rank_direction
				current_file += file_direction
			if self._is_color_peice_on_square(current_rank, current_file, color=opponent_color):
				threatened_moves.append((current_rank, current_file))

		return threatened_moves

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('k')
	def _threatened_moves_for_king(self, rank_index, file_index):
		opponent_color = self._opponent_of(
			self.get_peice_color_on_square(rank_index, file_index)
		)

		threatened_moves = []
		for rank_direction, file_direction in self._diagonals + self._straights:
			move_rank = rank_index + rank_direction
			move_file = file_index + file_direction
			if self._is_color_or_empty_square(move_rank, move_file, color=opponent_color):
				threatened_moves.append((move_rank, move_file))
		return threatened_moves

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('q')
	def _threatened_moves_for_queen(self, *args):
		return self._threatened_moves_for_sliding_peice(*args, straight=True, diagonal=True)

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('r')
	def _threatened_moves_for_rook(self, *args):
		return self._threatened_moves_for_sliding_peice(*args, straight=True)

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('b')
	def _threatened_moves_for_bishop(self, *args):
		return self._threatened_moves_for_sliding_peice(*args, diagonal=True)

	knight_deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('n')
	def _threatened_moves_for_knight(self, rank_index, file_index):
		opponent_color = self._opponent_of(self.get_peice_color_on_square(rank_index, file_index))

		threatened_moves = []
		for rank_delta, file_delta in self.knight_deltas:
			move_rank = rank_index + rank_delta
			move_file = file_index + file_delta
			if self._is_color_or_empty_square(move_rank, move_file, color=opponent_color):
				threatened_moves.append((move_rank, move_file))
		return threatened_moves

	@ChessBoardLegalMoveFunctionRegistrar.register_for_peice('p')
	def _threatened_moves_for_pawn(self, rank_index, file_index):
		opponent_color = self._opponent_of(
			self.get_peice_color_on_square(rank_index, file_index)
		)
		threatened_moves = []

		moves_with_needed_opponent_check = [
			((rank_index + 1, file_index + 1), True),
			((rank_index + 1, file_index - 1), True),
			((rank_index + 1, file_index), False)
		]
		for move_tuple, needs_opponent_in_square in moves_with_needed_opponent_check:
			if self._is_color_or_empty_square(*move_tuple, color=opponent_color):
				threatened_moves.append(move_tuple)

		return threatened_moves

	############################################################################
	# Magic Methods
	############################################################################

	class GetPeiceItemGetter(object):

		def __init__(self, board, first_index):
			self.board = board
			self.first_index = first_index

		def __getitem__(self, second_index):
			return self.board.get_peice(self.first_index, second_index)

		def __setitem__(self, second_index, value):
			self.board.set_peice(self.first_index, second_index, peice=value)

	class ChessBoardIterator(object):

		def __init__(self, board):
			self.board = board
			self.count = 0

		def __iter__(self):
			return self

		def next(self):
			if self.count < 64:
				peice_info = (
					(self.count/8, self.count % 8),
					self.board.get_peice(self.count/8, self.count % 8)
				)
				self.count += 1
				return peice_info
			raise StopIteration()


	def __getitem__(self, index):
		return self.GetPeiceItemGetter(self, index)

	def __iter__(self):
		return self.ChessBoardIterator(self)


class BasicChessBoard(ChessBoard):

	def __init__(self):
		self.reset_board()

	def reset_board(self):
		self._board = self._new_board
		self.action = self.WHITE
		self.white_king_position = (0, 4)
		self.black_king_position = (7, 4)

	def get_peice(self, rank_index, file_index):
		return self._board[rank_index][file_index]

	def set_peice(self, rank_index, file_index, peice=None):
		self._board[rank_index][file_index] = peice
		super(BasicChessBoard, self).set_peice(rank_index, file_index, peice=peice)


class DeltaChessBoard(ChessBoard):

	NOT_PRESENT = object()

	def __init__(self, parent):
		self.parent = parent
		self.reset_to_parent()

	def reset_to_parent(self):
		self.action = self.parent.action
		self.white_king_position = self.parent.white_king_position
		self.black_king_position = self.parent.black_king_position
		self.delta_dictionary = {}

	def get_peice(self, rank_index, file_index):
		peice = self.delta_dictionary.get((rank_index, file_index), self.NOT_PRESENT)
		if peice is self.NOT_PRESENT:
			return self.parent.get_peice(rank_index, file_index)
		return peice

	def set_peice(self, rank_index, file_index, peice=None):
		self.delta_dictionary[(rank_index, file_index)] = peice

	def make_new_with_move(self, source, dest):
		new_board = type(self)(self)
		new_board.make_move(source, dest)
		return new_board


class RecursiveDeltaChessBoard(DeltaChessBoard):

	def make_move(self, *args, **kwargs):
		return self.make_new_with_move(*args, **kwargs)
