from . import notation
from . import rules


class PlayableChessGame(object):

    def __init__(self):
        self._rules = rules.ChessRules()
        self._notation_processor = notation.ChessNotationProcessor(self._rules)

    def make_move_from_algebraic_and_return_uci(self, algebraic_move):
        return self.make_move_from_algebraic(algebraic_move).uci

    def make_move_from_algebraic(self, algebraic_move):
        move = self._notation_processor.parse_algebraic_move(algebraic_move)
        return self._rules.make_legal_move(move)
