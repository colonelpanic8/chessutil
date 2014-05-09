from .game import ChessGame
from .notation import ChessNotationProcessor

parse_long_uci_string = ChessNotationProcessor.parse_long_uci_string
del ChessNotationProcessor
