def file_to_index(file_char):
	return ord(file_char) - 97


def rank_to_index(rank):
	return rank - 1


def square_name_to_indices(square_name):
	file_char, rank_char = square_name
	return rank_to_index(int(rank_char)), file_to_index(file_char)


def make_eight(item):
	return [item for _ in range(8)]
