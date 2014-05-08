# -*- coding: utf-8 -*-
from __future__ import absolute_import
import itertools
import math

from . import common
from .position import Position


class DirectionalIterator(object):

    @Position.provide_position
    def __init__(self, position, rank_direction, file_direction):
          self.rank_index = position.rank_index
          self.file_index = position.file_index
          self.rank_direction = rank_direction
          self.file_direction = file_direction

    def next(self):
        self.rank_index += self.rank_direction
        self.file_index += self.file_direction
        try:
            return Position.from_rank_file(self.rank_index,
                                                  self.file_index)
        except common.IllegalPositionError:
            raise StopIteration()

    def __iter__(self):
        return self


class OneSquareIterator(DirectionalIterator):

    def next(self):
        position = super(OneSquareIterator, self).next()
        self.rank_index = -1
        self.file_index = -1
        self.rank_direction = 0
        self.file_direction = 0
        return position


class Piece(object):

    class __metaclass__(type):

        character_to_piece_class = {}

        def __init__(cls, *args):
            type.__init__(cls, *args)
            if cls.character is not None:
                cls.character_to_piece_class[cls.character.lower()] = cls

        @classmethod
        def get_piece_class(cls, piece_char_or_class):
            if isinstance(piece_char_or_class, basestring):
                return cls.character_to_piece_class[piece_char_or_class.lower()]
            assert isinstance(piece_char_or_class, Piece)
            return piece_char_or_class

        @classmethod
        def get_promotion_class(cls, incoming):
            if incoming is None:
                return None
            piece_class = cls.get_piece_class(incoming)
            assert piece_class not in (King, Pawn)
            return piece_class

    character = None
    directions = None
    move_iterator_class = None
    piece_finder_class = None
    is_empty = False
    black_unicode_string = None
    white_unicode_string = None

    @classmethod
    @Position.provide_position
    def move_iterators(cls, position, invert_direction=False):
        for rank_direction, file_direction in cls.directions:
            if invert_direction:
                rank_direction *= -1
                file_direction *= -1
            yield cls.move_iterator_class(position, rank_direction,
                                          file_direction)


    def __init__(self, color):
        self.color = color

    @property
    def name(self):
        return self.character.upper() if self.color == common.color.BLACK \
            else self.character.lower()

    @property
    def move_prefix(self):
        return self.name.upper()

    @classmethod
    def find(cls, destination_position, chess_board, color=None, source_rank=None,
             source_file=None, find_all=False):
        finder = cls.piece_finder_class(chess_board, cls, color, find_all)
        return finder.find(destination_position, source_rank, source_file)

    @Position.provide_position
    def get_all_threatened_moves(self, position, chess_board):
        return itertools.chain(self._get_normal_threatened_moves(position,
                                                                 chess_board),
                               self._get_special_threatened_moves(position,
                                                                  chess_board))

    def _get_normal_threatened_moves(self, position, chess_board):
        for move_iterator in self.move_iterators(position):
            for test_position in move_iterator:
                piece = chess_board[test_position]
                if piece.color == self.color:
                    break
                yield test_position
                if piece.color == self.color.opponent:
                    break

    def _get_special_threatened_moves(self, position, chess_board):
        return []

    def __str__(self):
        return self.name

    @property
    def unicode_string(self):
        return (self.white_unicode_string
                if self.color == common.color.WHITE else
                self.black_unicode_string)

    def build_disambiguation(self, chess_board, move):
        piece_in_same_rank = False
        piece_in_same_file = False
        found_positions = self.find(move.destination, chess_board,
                                    color=self.color, find_all=True)

        if len(found_positions) < 2:
            return ''

        for position in found_positions:
            if position == move.source: continue
            if position.rank_index == move.source.rank_index:
                piece_in_same_rank = True
            if position.file_index == move.source.file_index:
                piece_in_same_file = True

        if piece_in_same_rank and piece_in_same_file:
            return move.source.algebraic

        if not piece_in_same_file:
            return common.index_to_file(move.source.file_index)

        return common.index_to_rank(move.source.rank_index)

    def __eq__(self, other):
        return type(self) == type(other) and self.color == other.color


class PieceFinder(object):

    def __init__(self, chess_board, piece_class, color, find_all=False):
        self.chess_board = chess_board
        self.piece_class = piece_class
        self.color = color
        self.find_all = find_all

    def _piece_matches(self, piece):
        return piece.color == self.color and type(piece) == self.piece_class


class NormalPieceFinder(PieceFinder):

    @Position.provide_position
    def find(self, destination_position, source_rank=None, source_file=None):
        rank_delta = None if source_rank is None else \
                     source_rank - destination_position.rank_index
        file_delta = None if source_file is None else \
                     source_file - destination_position.file_index

        def direction_matches(rank_direction, file_direction):
            if rank_delta is not None and rank_direction != rank_delta:
                return None
            if file_delta is not None and file_direction != file_delta:
                return None

            try:
                test_position = destination_position.delta(rank_direction,
                                                           file_direction)
            except common.IllegalPositionError:
                return None

            if self._piece_matches(self.chess_board[test_position]):
                return test_position

        if self.find_all:
            return self._find_all(direction_matches)
        else:
            return [self._find_one(direction_matches)]

    @common.listify
    def _find_all(self, direction_matches):
        for direction in self.piece_class.directions:
            position = direction_matches(*direction)
            if position is not None:
                yield position

    def _find_one(self, direction_matches):
        for direction in self.piece_class.directions:
            position = direction_matches(*direction)
            if position is not None:
                return position


class NormalPiece(Piece):

    move_iterator_class = OneSquareIterator
    piece_finder_class = NormalPieceFinder


class SlidingPieceFinder(PieceFinder):

    @Position.provide_position
    def find(self, destination_position, source_rank=None, source_file=None):
        if self._can_use_find_simple(destination_position,
                                     source_rank, source_file):
            return self._find_simple(destination_position,
                                     source_rank, source_file)

        move_iterators = self.piece_class.move_iterators_matching(
            destination_position, source_rank, source_file
        )
        if self.find_all:
            return self._find_all(move_iterators)
        else:
            return self._find_one(move_iterators)

    @common.listify
    def _find_all(self, move_iterators):
        for move_iterator in move_iterators:
            position = self._find_using_move_iterator(move_iterator)
            if position is not None:
                yield position

    def _find_one(self, move_iterators):
        for move_iterator in move_iterators:
            position = self._find_using_move_iterator(move_iterator)
            if position is not None:
                return [position]
        return []

    def _can_use_find_simple(self, destination_position, source_rank, source_file):
        # We can't use find simple if the destination[rank, file] is the same as the
        # source[rank, file] because there is no way to triangulate in that case.
        return (
            source_rank is not None and
            source_rank != destination_position.rank_index
        ) or (
            source_file is not None and
            source_file != destination_position.file_index
        )

    def _find_using_move_iterator(self, move_iterator):
        for position in move_iterator:
            piece = self.chess_board[position]
            if self._piece_matches(piece):
                return position
            elif piece.color != common.color.NONE:
                return None
        else:
            return None

    def _find_simple(self, destination_position, source_rank, source_file):
        assert not (source_rank is None and source_file is None)
        rank_delta = None if source_rank is None else \
                     source_rank - destination_position.rank_index
        file_delta = None if source_file is None else \
                     source_file - destination_position.file_index

        directions = self.piece_class.directions

        if rank_delta is not None:
            directions = [direction for direction in directions
                          if math.copysign(rank_delta, direction[0]) == rank_delta]
            magnitude = abs(rank_delta);

        if file_delta is not None:
            directions = [direction for direction in directions
                          if math.copysign(file_delta, direction[1]) == file_delta]
            magnitude = abs(file_delta);

        for rank_direction, file_direction in directions:
            try:
                position = destination_position.delta(rank_direction * magnitude,
                                                      file_direction * magnitude)
            except common.IllegalPositionError:
                pass
            else:
                if self._piece_matches(self.chess_board[position]):
                    return [position]


class SlidingPiece(Piece):

    move_iterator_class = DirectionalIterator
    piece_finder_class = SlidingPieceFinder

    @classmethod
    @Position.provide_position
    def move_iterators_matching(cls, destination_position,
                                source_rank=None, source_file=None):
        move_iterators = cls.move_iterators(destination_position)

        if source_rank is not None:
            move_iterators = [move_iterator
                              for move_iterator in move_iterators
                              if move_iterator.rank_direction == 0]

        if source_file is not None:
            move_iterators = [move_iterator
                              for move_iterator in move_iterators
                              if move_iterator.file_direction == 0]
        return move_iterators


_diagonals = ((-1, 1), (1, -1), (1, 1), (-1, -1))
_straights = ((1,  0), (-1, 0), (0, 1), (0,  -1))
_back_rank_squares = {common.color.WHITE: 0, common.color.BLACK: 7}


class King(NormalPiece):

    character = 'k'
    white_unicode_string = u'♔'
    black_unicode_string = u'♚'
    directions = _diagonals + _straights

    @property
    def back_rank(self):
        return _back_rank_squares[self.color]

    def _get_special_threatened_moves(self, position, chess_rules):
        if position.rank_index != self.back_rank:
            raise StopIteration()
        if chess_rules.can_castle_kingside(self.color) and all(
            chess_rules[position.replace(file_index=file_index)].is_empty
            for file_index in range(5, 7)
        ):
             yield position.replace(file_index=6)

        if chess_rules.can_castle_queenside(self.color) and all(
            chess_rules[position.replace(file_index=file_index)].is_empty
            for file_index in range(1, 4)
        ):
            yield position.replace(file_index=2)

    def build_disambiguation(self, *args):
        return ''


class Queen(SlidingPiece):

    character = 'q'
    white_unicode_string = u'♕'
    black_unicode_string = u'♛'
    directions = _diagonals + _straights


class Rook(SlidingPiece):

    character = 'r'
    white_unicode_string = u'♖'
    black_unicode_string = u'♜'
    directions = _straights


class Bishop(SlidingPiece):

    character = 'b'
    white_unicode_string = u'♗'
    black_unicode_string = u'♝'
    directions = _diagonals


class Knight(NormalPiece):

    character = 'n'
    white_unicode_string = u'♘'
    black_unicode_string = u'♞'
    directions = [(1,  2), (2,  1), (-1,  2), (-2,  1),
                  (1, -2), (2, -1), (-1, -2), (-2, -1)]


class Pawn(Piece):

    move_prefix = ''
    character = 'p'
    white_unicode_string = u'♙'
    black_unicode_string = u'♟'
    _enpassant_squares = {
        common.color.WHITE: 4,
        common.color.BLACK: 3
    }

    @classmethod
    def move_iterators(*args, **kwargs):
        return []

    @Position.provide_position
    def _get_special_threatened_moves(self, position, chess_board):
        new_rank_index = position.rank_index + self.color
        for new_file_index in (-1 + position.file_index, 1 + position.file_index):
            try:
                new_position = Position.from_rank_file(new_rank_index, new_file_index)
            except common.IllegalPositionError:
                continue
            if (chess_board[new_position].color == self.color * -1 or
                self.is_enpassant_available(position, new_position, chess_board)):
                yield new_position
        new_position = position.replace(new_rank_index)
        if chess_board[new_position].is_empty:
            yield new_position
        else:
            # Break here because we can't do the double pawn move either.
            raise StopIteration()

        # Check for double pawn move.
        if position.rank_index == _back_rank_squares[self.color] + self.color:
            new_position = position.delta(self.color * 2)
            if chess_board[new_position].is_empty:
                yield new_position

    @property
    def enpassant_square(self):
        return self._enpassant_squares[self.color]

    def is_enpassant_available(self, position, new_position, chess_board):
        if position.rank_index != self.enpassant_square:
            return False

        if chess_board.moves:
            last_move = chess_board.moves[-1]
        else:
            return False

        return (type(last_move.piece) == type(self) and
                last_move.source.file_index == new_position.file_index and
                last_move.source.rank_index == new_position.rank_index + self.color and
                last_move.destination.rank_index == new_position.rank_index - self.color)

    def build_disambiguation(self, chess_board, move):
        return "" if move.source.file_index == move.destination.file_index else \
            common.index_to_file(move.source.file_index)


class Empty(object):

    class __metaclass__(type):

        def __str__(cls):
            return cls.character

    is_empty = True
    color = common.color.NONE
    character = u'.'
    unicode_string = character


    def get_all_threatened_moves(self, *args):
        return None


_back_rank_classes = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]


def build_back_rank(color):
    return map(lambda piece_class: piece_class(color), _back_rank_classes)


def build_pawn_rank(color):
    return [Pawn(color) for _ in range(8)]