def clear_everything_but_kings_from_board(board):
	for square_tuple, piece in board:
		if piece and piece.lower() != 'k':
			board.set_piece(*square_tuple)
