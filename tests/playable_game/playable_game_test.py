from . import *
from playable_game import playable_game

class PlayableChessGameTestCase(T.TestCase):

	moves = ["e4", "e5", "Nf3", "Nc6", "Bc4", "d6", "c3", "a6", "d4", "exd4", "cxd4", "Bd7", "Nc3", "Na5", "Bxf7+", "Kxf7", "Ng5+", "Ke8", "Qf3", "Qf6", "Bf4", "Ne7", "O-O", "h6", "e5", "Qg6", "exd6", "hxg5", "dxe7", "gxf4", "exf8=Q+", "Rxf8", "Rae1+", "Kd8", "Nd5", "Qc6", "Rc1", "Qd6", "Nxc7", "Rc8", "Nd5", "Bc6", "Rfe1", "Bxd5", "Rxc8+", "Kxc8", "Qg4+", "Qd7", "Rc1+", "Kd8", "Qg5+", "Qe7", "Rc8+", "Kd7", "Rc7+", "Kxc7", "Qxe7+"]

	@T.let
	def playable_game(self):
		return playable_game.PlayableChessGame()

	def test_moves(self):
		for move in self.moves:
			print move,
			print self.playable_game.make_move_from_algebraic_and_return_uci(move)
			self.playable_game._board.print_board()
