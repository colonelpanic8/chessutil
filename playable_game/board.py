from __future__ import absolute_import

from . import common


class ChessBoard(object):

	############################################################################
	# Mandatory Override Methods
	############################################################################

	def get_piece(self, rank_index, file_index):
		raise NotImplemented()

	def set_piece(self, rank_index, file_index, piece=None):
		if piece == 'k':
			self.white_king_position = (rank_index, file_index)
		elif piece == 'K':
			self.black_king_position = (rank_index, file_index)

	############################################################################
	# Public Methods
	############################################################################

	def get_piece_color(self, piece):
		return common._bool_or_none_to_color_map[self._is_piece_white(piece)]

	def make_move(self, source, dest, piece):
		self.set_piece(*dest, piece=piece)
		self.set_piece(*source)

	def get_piece_color_on_square(self, rank_index, file_index):
		return common._bool_or_none_to_color_map[
			self._is_piece_on_square_white(rank_index, file_index)
		]

	def is_legal_square(self, rank_index, file_index):
		return 0 <= rank_index < 8 and 0 <= file_index < 8

	def is_color_or_empty_square(self, rank_index, file_index, color=common.WHITE):
		return self.is_color_piece_on_square(rank_index, file_index, color=color) or self.is_empty_square(rank_index, file_index)

	def is_color_piece_on_square(self, rank_index, file_index, color=common.WHITE):
		return self.is_legal_square(rank_index, file_index) and \
			self.get_piece_color_on_square(rank_index, file_index) == color

	def is_empty_square(self, rank_index, file_index):
		return self.is_legal_square(rank_index, file_index) and \
			self.get_piece_color_on_square(rank_index, file_index) == common.NONE

	def get_king_postion_for_color(self, color=None):
		if color == common.WHITE:
			return self.white_king_position
		if color == common.BLACK:
			return self.black_king_position

	horizontal_table_border = "  +-----------------+"

	def print_board(self):
		print self.horizontal_table_border
		for rank_index in range(8)[::-1]:
			row = [
				self.get_piece(rank_index, file_index) for file_index in range(8)
			]
			print "{0} | {1} {2} {3} {4} {5} {6} {7} {8} |".format(
				rank_index + 1,
				*map(lambda x: "." if x is None else x, row)
			)
		print self.horizontal_table_border
		print "    A B C D E F G H"

	############################################################################
	# Private Methods
	############################################################################

	def _is_piece_on_square_white(self, rank_index, file_index):
		if not self.is_legal_square(rank_index, file_index):
			raise IllegalSquareError()
		return self._is_piece_white(self.get_piece(rank_index, file_index))

	def _is_piece_white(self, piece):
		if piece:
			return piece.islower()
		else:
			return None

	@property
	def _new_board(self):
		return [
			['r','n','b','q','k','b','n','r'],
			common.make_eight('p'),
			common.make_eight(None),
			common.make_eight(None),
			common.make_eight(None),
			common.make_eight(None),
			common.make_eight('P'),
			['R','N','B','Q','K','B','N','R']
		]

	############################################################################
	# Magic Methods
	############################################################################

	def __getitem__(self, index):
		return self.GetPieceItemGetter(self, index)

	def __iter__(self):
		return self.ChessBoardIterator(self)


	class GetPieceItemGetter(object):

		def __init__(self, board, first_index):
			self.board = board
			self.first_index = first_index

		def __getitem__(self, second_index):
			return self.board.get_piece(self.first_index, second_index)

		def __setitem__(self, second_index, value):
			self.board.set_piece(self.first_index, second_index, piece=value)


	class ChessBoardIterator(object):

		def __init__(self, board):
			self.board = board
			self.count = 0

		def __iter__(self):
			return self

		def next(self):
			if self.count < 64:
				piece_info = (
					(self.count/8, self.count % 8),
					self.board.get_piece(self.count/8, self.count % 8)
				)
				self.count += 1
				return piece_info
			raise StopIteration()


class BasicChessBoard(ChessBoard):

	def __init__(self):
		self.reset_board()

	def reset_board(self):
		self._board = self._new_board
		self.white_king_position = (0, 4)
		self.black_king_position = (7, 4)

	def get_piece(self, rank_index, file_index):
		return self._board[rank_index][file_index]

	def set_piece(self, rank_index, file_index, piece=None):
		self._board[rank_index][file_index] = piece
		super(BasicChessBoard, self).set_piece(rank_index, file_index, piece=piece)


class DeltaChessBoard(ChessBoard):

	NOT_PRESENT = object()

	def __init__(self, parent):
		self.parent = parent
		self.reset_to_parent()

	def reset_to_parent(self):
		self.white_king_position = self.parent.white_king_position
		self.black_king_position = self.parent.black_king_position
		self.delta_dictionary = {}

	def get_piece(self, rank_index, file_index):
		piece = self.delta_dictionary.get((rank_index, file_index), self.NOT_PRESENT)
		if piece is self.NOT_PRESENT:
			return self.parent.get_piece(rank_index, file_index)
		return piece

	def set_piece(self, rank_index, file_index, piece=None):
		self.delta_dictionary[(rank_index, file_index)] = piece
		super(DeltaChessBoard, self).set_piece(rank_index, file_index, piece=piece)
