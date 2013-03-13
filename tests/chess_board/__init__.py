def clear_everything_but_kings_from_board(board):
	for square_tuple, peice in board:
		if peice and peice.lower() != 'k':
			board.set_peice(*square_tuple)
