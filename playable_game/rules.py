from __future__ import absolute_import
import functools

from . import board
from . import common


class ChessRulesFunctionRegistrar(type):

	piece_to_threatened_function_map = {}
	piece_to_find_function_map = {}

	def __init__(self, *args, **kwargs):
		self._piece_to_threatened_function_map = self.piece_to_threatened_function_map
		self._piece_to_find_function_map = self.piece_to_find_function_map
		super(ChessRulesFunctionRegistrar, self).__init__(*args, **kwargs)

	@classmethod
	def register_threatened_move_function(cls, function, piece):
		cls.piece_to_threatened_function_map[piece] = function
		return function

	@classmethod
	def register_threatened_for_piece(cls, piece):
		return functools.partial(cls.register_threatened_move_function, piece=piece)

	@classmethod
	def register_find_piece_function(cls, function, piece):
		cls.piece_to_find_function_map[piece] = function
		return function

	@classmethod
	def register_find_for_piece(cls, piece):
		return functools.partial(cls.register_find_piece_function, piece=piece)


class ChessRules(object):

	__metaclass__ = ChessRulesFunctionRegistrar

	def __init__(self, board=None):
		if board == None:
			board = board.BasicChessBoard()
		self._board = board
		self.action = common.WHITE
		self.moves = []
		self._white_can_castle_kingside = True
		self._black_can_castle_kingside = True
		self._white_can_castle_queenside = True
		self._black_can_castle_queenside = True

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
				if self._board.get_piece_color_on_square(i, j) == by_color and \
				   square in set(self._get_squares_threatened_by(i, j)):
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
				raise common.IllegalMoveError("You must specify a valid promotion.")
			else:
				piece = move_info.promotion
				if self.action == common.WHITE:
					piece = piece.lower()
		elif move_info.promotion is not None:
			raise common.IllegalMoveError("Promotion not allowed for this move.")

		if piece.lower() == 'k':
			if move_info.source[1] == 4:
				if move_info.destination[1] == 6:
					# Kingside castle.
					self._board.make_move(
						(move_info.source[0], 7),
						(move_info.source[0], 5)
					)
				if move_info.destination[1] == 2:
					# Queenside castle.
					self._board.make_move(
						(move_info.source[0], 0),
						(move_info.source[0], 3)
					)
				# Disable castling after a king move no matter what.
				if self.action == common.WHITE:
					self._white_can_castle_queenside = False
					self._white_can_castle_kingside = False
				else:
					self._black_can_castle_queenside = False
					self._black_can_castle_kingside = False

		if piece.lower() == 'p' and move_info.destination[1] != move_info.source[1] and \
		   self._board.is_empty_square(*move_info.destination):
			self._board.set_piece(move_info.source[0], move_info.destination[1])

		if move_info.source == (0, 0):
			self._white_can_castle_queenside = False
		if move_info.source == (0, 7):
			self._white_can_castle_kingside = False
		if move_info.source == (7, 0):
			self._black_can_castle_queenside = False
		if move_info.source == (7, 7):
			self._black_can_castle_kingside = False

		self._board.make_move(move_info.source, move_info.destination, piece)
		self.action = common.opponent_of(self.action)
		self.moves.append(move_info)

	def find_piece(self, piece, destination, *args, **kwargs):
		return self._get_find_function_for_piece(piece)(self, piece, *destination, **kwargs)

	def can_castle_kingside(self, color):
		return self._white_can_castle_kingside if color == common.WHITE \
			else self._black_can_castle_kingside

	def can_castle_queenside(self, color):
		return self._white_can_castle_queenside if color == common.WHITE \
			else self._black_can_castle_queenside

	############################################################################
	# Private Methods
	############################################################################

	def _get_legal_moves_function_for_piece(self, piece):
		return self._piece_to_threatened_function_map[piece.lower()]

	def _get_find_function_for_piece(self, piece):
		return self._piece_to_find_function_map[piece.lower()]

	def _get_squares_threatened_by(self, rank_index, file_index):
		piece = self._board.get_piece(rank_index, file_index)
		return self._get_legal_moves_function_for_piece(piece)(self, rank_index, file_index)

	def _filter_moves_for_king_safety(self, start_position, moves):
		moves = set(moves)
		piece = self._board.get_piece(*start_position)
		piece_color = self._board.get_piece_color_on_square(*start_position)
		delta_board = board.DeltaChessBoard(self._board)
		delta_rules = ChessRules(delta_board)

		if piece.lower() == 'k':
			back_rank_index = 0 if piece_color is common.WHITE else 7
			if start_position == (back_rank_index, 4):
				castling_square = (back_rank_index, 6)
				if castling_square in moves and any(
					self.is_square_threatened(
						(back_rank_index, file_index),
						by_color=common.opponent_of(piece_color)
					) for file_index in range(4, 7)
				):
					moves.remove(castling_square)
				castling_square = (back_rank_index, 2)
				if castling_square in moves and any(
					self.is_square_threatened(
						(back_rank_index, file_index),
						by_color=common.opponent_of(piece_color)
					) for file_index in range(2, 5)
				):
					moves.remove(castling_square)
		else:
			# Do an initial check to see if we can avoid checking every move.
			delta_board.set_piece(*start_position)
			if not delta_rules.is_square_threatened(
				delta_board.get_king_postion_for_color(piece_color),
				by_color=common.opponent_of(piece_color)
			):
				return moves

		king_safe_moves = []
		for move in moves:
			delta_board.reset_to_parent()
			delta_board.make_move(start_position, move, piece)
			if not delta_rules.is_square_threatened(
				delta_board.get_king_postion_for_color(piece_color),
				by_color=common.opponent_of(piece_color)
			):
				king_safe_moves.append(move)

		return king_safe_moves

	_diagonals = [(-1, 1), (1, -1), (1, 1), (-1, -1)]
	_straights = [(1, 0), (-1, 0), (0, 1), (0, -1)]
	_knight_deltas = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]

	############################################################################
	# Theatened Moves Methods
	############################################################################

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

	def _get_castling_moves_for_color(self, color):
		back_rank = 0 if color is common.WHITE else 7
		if self.can_castle_kingside(color) and all(
			self._board.is_empty_square(back_rank, file_index)
			for file_index in range(5, 7)
		):
			yield (back_rank, 6)
		if self.can_castle_queenside(color) and all(
			self._board.is_empty_square(back_rank, file_index)
			for file_index in range(2, 4)
		):
			yield (back_rank, 2)

	@ChessRulesFunctionRegistrar.register_threatened_for_piece('k')
	def _threatened_moves_for_king(self, rank_index, file_index):
		piece_color = self._board.get_piece_color_on_square(rank_index, file_index)

		threatened_moves = []
		for rank_direction, file_direction in self._diagonals + self._straights:
			move_rank = rank_index + rank_direction
			move_file = file_index + file_direction
			if self._board.is_color_or_empty_square(
				move_rank,
				move_file,
				color=common.opponent_of(piece_color)
			):
				threatened_moves.append((move_rank, move_file))

		threatened_moves.extend(self._get_castling_moves_for_color(piece_color))
		return threatened_moves

	@ChessRulesFunctionRegistrar.register_threatened_for_piece('q')
	def _threatened_moves_for_queen(self, *args):
		return self._threatened_moves_for_sliding_piece(*args, straight=True, diagonal=True)

	@ChessRulesFunctionRegistrar.register_threatened_for_piece('r')
	def _threatened_moves_for_rook(self, *args):
		return self._threatened_moves_for_sliding_piece(*args, straight=True)

	@ChessRulesFunctionRegistrar.register_threatened_for_piece('b')
	def _threatened_moves_for_bishop(self, *args):
		return self._threatened_moves_for_sliding_piece(*args, diagonal=True)

	@ChessRulesFunctionRegistrar.register_threatened_for_piece('n')
	def _threatened_moves_for_knight(self, rank_index, file_index):
		opponent_color = common.opponent_of(
			self._board.get_piece_color_on_square(rank_index, file_index)
		)

		threatened_moves = []
		for rank_delta, file_delta in self._knight_deltas:
			move_rank = rank_index + rank_delta
			move_file = file_index + file_delta
			if self._board.is_color_or_empty_square(move_rank, move_file, color=opponent_color):
				threatened_moves.append((move_rank, move_file))
		return threatened_moves

	def _check_pawn_capture_move(self, rank_index, file_index, color=common.WHITE):
		if not self._board.is_legal_square(rank_index, file_index):
			return False
		return self._board.is_color_piece_on_square(
			rank_index,
			file_index,
			color=common.opponent_of(color)
		) or self._is_enpassant_available(rank_index, file_index, color)

	def _is_enpassant_available(self, rank_index, file_index, color):
		if not self.moves:
			return False
		pawn_to_take_position = (rank_index + (color * -1), file_index)
		piece = self._board.get_piece(*pawn_to_take_position)
		return self.moves[-1] == common.MoveInfo(
			(rank_index + color, file_index),
			pawn_to_take_position
		) and piece and piece.lower() == 'p'

	@ChessRulesFunctionRegistrar.register_threatened_for_piece('p')
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
				lambda r, f: r == double_move_rank and \
				self._board.is_empty_square(r, f) and \
				self._board.is_empty_square(r - piece_color, f)
			)
		]
		for move_tuple, predicate in moves_with_predicates:
			if predicate(*move_tuple):
				threatened_moves.append(move_tuple)

		return threatened_moves

	############################################################################
	# Find Piece Methods
	############################################################################

	_piece_to_straight_diagonal_tuples = {
		'q': (True, True),
		'b': (False, True),
		'r': (True, False),
	}

	def _find_piece_in_squares(self, piece, squares):
		for square in squares:
			if self._board.is_legal_square(*square) and self._board.get_piece(*square) == piece:
				return square
		raise common.PieceNotFoundError()

	def _find_sliding_piece(
		self,
		piece,
		destination_rank,
		destination_file,
		source_rank=None,
		source_file=None,
	):
		directions = []
		straight, diagonal = self._piece_to_straight_diagonal_tuples[piece.lower()]
		if source_rank is not None:
			if source_rank == destination_rank:
				assert straight
				directions = [(0, 1), (0, -1)]
			else:
				squares_to_check = []
				if straight:
					squares_to_check.append((source_rank, destination_file))
				if diagonal:
					rank_difference = destination_rank - source_rank
					squares_to_check += [
						(source_rank, destination_file + rank_difference),
						(source_rank, destination_file - rank_difference)
					]
				return self._find_piece_in_squares(piece, squares_to_check)
		elif source_file is not None:
			if source_file == destination_file:
				assert straight
				directions = [(1, 0), (-1, 0)]
			else:
				squares_to_check = []
				if straight:
					squares_to_check.append((destination_rank, source_file))
				if diagonal:
					file_difference = destination_file - source_file
					squares_to_check += [
						(destination_rank + file_difference, source_file),
						(destination_rank - file_difference, source_file)
					]
				return self._find_piece_in_squares(piece, squares_to_check)
		else:
			if diagonal:
				directions.extend(self._diagonals)
			if straight:
				directions.extend(self._straights)

		for rank_direction, file_direction in directions:
			current_rank = destination_rank + rank_direction
			current_file = destination_file + file_direction
			while self._board.is_empty_square(current_rank, current_file):
				current_rank += rank_direction
				current_file += file_direction

			square = (current_rank, current_file)
			if self._board.is_legal_square(*square) and self._board.get_piece(*square) == piece:
				return square

		raise common.PieceNotFoundError()

	_find_queen = ChessRulesFunctionRegistrar.register_find_for_piece('q')(_find_sliding_piece)
	_find_rook = ChessRulesFunctionRegistrar.register_find_for_piece('r')(_find_sliding_piece)
	_find_bishop = ChessRulesFunctionRegistrar.register_find_for_piece('b')(_find_sliding_piece)

	@ChessRulesFunctionRegistrar.register_find_for_piece('k')
	def _find_king(self, *args, **kwargs):
		return self._board.get_king_postion_for_color(self.action)

	@ChessRulesFunctionRegistrar.register_find_for_piece('n')
	def _find_knight(
		self,
		piece,
		destination_rank,
		destination_file,
		source_rank=None,
		source_file=None,
	):
		if source_rank is not None:
			rank_difference = source_rank - destination_rank
			deltas_to_check = [
				delta for delta in self._knight_deltas
				if delta[0] == rank_difference
			]
		elif source_file is not None:
			file_difference = source_file - destination_file
			deltas_to_check = [
				delta for delta in self._knight_deltas
				if delta[1] == file_difference
			]
		else:
			deltas_to_check = self._knight_deltas

		squares_to_check = map(
			lambda delta: (lambda r, f: (r+destination_rank, f+destination_file))(*delta),
			deltas_to_check
		)

		return self._find_piece_in_squares(piece, squares_to_check)
