from . import common


def file_to_index(file_char):
	return ord(file_char) - 97


def rank_to_index(rank):
	return rank - 1


def square_name_to_indices(square_name):
	file_char, rank_char = square_name
	return rank_to_index(int(rank_char)), file_to_index(file_char)



class NotationProcessor(object):

	def make_move_with_uci_notation(self, move):
		return self.make_move_with_square_names(move[:2], move[2:])

	def make_move_with_square_names(self, source, dest):
		return self.make_move(
			common.square_name_to_indices(source),
			common.square_name_to_indices(dest)
		)

	def parse_algebraic_move(self, board, algebraic_move):
		algebraic_move = algebraic_move.strip()

		# Handle Castling
		if algebraic_move == "O-O":
			if self.action == self.WHITE:
				return ((0, 4), (0, 6))
			else:
				return ((7, 4), (7, 6))

		if algebraic_move == "O-O-O":
			if self.action == self.WHITE:
				return ((4, 0), (2, 0))
			else:
				return ((4, 7), (2, 7))

	re.compile()

	def parse_pawn_move(self, algebraic_move):
        # Clean up the textmove
		"".join(algebraic_move.split("e.p."))

		move_characters = [
			character for character in algebraic_move
			if character in set("KQRNBabcdefgh12345678")
		]

		if len(t) < 2:
			raise

        # Get promotion if any
		if t[-1] in ('Q','R','N','B'):
			promotion = {'Q':1,'R':2,'N':3,'B':4}[t.pop()]

		if len(t) < 2:
			return None

        # Get the destination
		if not files.has_key(t[-2]) or not ranks.has_key(t[-1]):
			return None

        dest_x = files[t[-2]]
		dest_y = ranks[t[-1]]

        # Pick out the hints
		t = t[:-2]
		for h in t:
			if h in ('K','Q','R','N','B','P'):
				h_piece = h
			elif h in ('a','b','c','d','e','f','g','h'):
				h_file = files[h]
			elif h in ('1','2','3','4','5','6','7','8'):
				h_rank = ranks[h]

        # If we have both a source and destination we don't need the piece hint.
		# This will make us make the move directly.
		if h_rank > -1 and h_file > -1:
			h_piece = None

		return (h_piece,h_file,h_rank,dest_x,dest_y,promotion)
