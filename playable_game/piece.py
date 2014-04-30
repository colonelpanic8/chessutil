from __future__ import absolute_import
import itertools
import math

from . import common

provide_position = common.Position.provide_position


class DirectionalIterator(object):

    @provide_position
    def __init__(self, position, rank_direction, file_direction):
          self.rank_index = position.rank_index
          self.file_index = position.file_index
          self.rank_direction = rank_direction
          self.file_direction = file_direction

    def next(self):
        self.rank_index += self.rank_direction
        self.file_index += self.file_direction
        try:
            return common.Position.from_rank_file(self.rank_index, self.file_index)
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

    character = None
    directions = None
    is_empty = False
    move_iterator_class = None

    @classmethod
    @common.listify
    @provide_position
    def move_iterators(cls, position, invert_direction=False):
        for rank_direction, file_direction in cls.directions:
            if invert_direction:
                rank_direction *= -1
                file_direction *= -1
            yield cls.move_iterator_class(position, rank_direction, file_direction)


    def __init__(self, color, chess_board):
        self.color = color
        self.chess_board = chess_board

    @property
    def name(self):
        return self.character.upper() if self.color == common.BLACK \
            else self.character

    def find(self, destination_position, color=None, source_rank=None,
             source_file=None, find_all=False):
        raise NotImplementedError()

    @provide_position
    def get_all_threatened_moves(self, position, chess_board):
        return itertools.chain(self._get_normal_threatened_moves(position,
                                                                 chess_board),
                               self._get_special_threatened_moves(position,
                                                                  chess_board))

    def _get_normal_threatened_moves(self, position, chess_board):
        for move_iterator in self.move_iterators(position):
            for test_position in move_iterator:
                piece = chess_board[test_position]
                if piece.color == common.NONE:
                    yield test_position
                elif piece.color == self.color:
                    break
                else:
                    yield test_position
                    break

    def _get_special_threatened_moves(self, position, chess_board):
        return []


class PieceFinder(object):

    def __init__(self, chess_board, piece_class, color, find_all=False):
        self.chess_board = chess_board
        self.piece_class = piece_class
        self.color = color
        self.find_all = find_all


class NormalPiece(object):

    move_iterator_class = OneSquareIterator


class NormalPieceFinder(object):

    @provide_position
    def find(self, destination_position, source_rank=None, source_file=None):
        rank_delta = None if source_rank is None else \
                     source_rank - destination_position.rank
        file_delta = None if source_file is None else \
                     source_file - destination_position.file

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

            if self.chess_board[test_position].is_of_color(self.color):
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


class SlidingPiece(object):

    move_iterator_class = DirectionalIterator

    @classmethod
    @provide_position
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


class SlidingPieceFinder(object):

    @provide_position
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

    def _can_use_find_simple(destination_position, source_rank, source_file):
        return (
            source_rank is not None and
            source_rank != destination_position.rank
        ) or (
            source_file is not None and
            source_file != destination_position.file
        )

    def _find_using_move_iterator(self, move_iterator):
        for position in move_iterator:
            piece = self.chess_board.get(position)
            if piece.color == self.color:
                return position
            elif piece.color != common.NONE:
                return None
        else:
            return None

    def _find_simple(self, destination_position, source_rank, source_file):
        assert not (source_rank is None and source_file is None)
        rank_delta = None if source_rank is None else \
                     source_rank - destination_position.rank
        file_delta = None if source_file is None else \
                     source_file - destination_position.file

        directions = self.peice_class.directions

        if rank_delta is not None:
            directions = [direction for direction in directions
                          if math.copysign(rank_delta, direction) == rank_delta]
            magnitude = abs(rank_delta);

        if file_delta is not None:
            directions = [direction for direction in directions
                          if math.copysign(file_delta, direction) == file_delta]
            magnitude = abs(file_delta);

        for rank_direction, file_direction in self.directions:
            try:
                position = destination_position.delta(rank_direction * magnitude,
                                                      file_direction * magnitude)
            except common.IllegalSquareError():
                pass
            if self.chess_board[position].color == self.color:
                return position


_diagonals = ((-1, 1), (1, -1), (1, 1), (-1, -1))
_straights = ((1,  0), (-1, 0), (0, 1), (0,  -1))
_back_rank_squares = {common.WHITE: 0, common.BLACK: 7}



class King(NormalPiece):

    directions = _diagonals + _straights

    @property
    def back_rank(self):
        return _back_rank_squares[self.color]

    def _get_special_threatened_moves(self, position, chess_board):
        if self.position.rank_index != self.back_rank:
            raise StopIteration()
        if chess_board.can_castle_kingside(self.color) and all(
            chess_board[position.replace(file_index=file_index)].is_empty
            for file_index in range(5, 7)
        ):
             yield position.replace(file_index=6)

        if chess_board.can_castle_queenside(self.color) and all(
            chess_board[position.replace(file_index=file_index)].is_empty
            for file_index in range(1, 4)
        ):
            yield position.replace(file_index=2)


class Queen(SlidingPiece):

    directions = _diagonals + _straights


class Rook(SlidingPiece):

    directions = _straights


class Bishop(SlidingPiece):

    directions = _diagonals


class Knight(NormalPiece):

    directions = [(1,  2), (2,  1), (-1,  2), (-2,  1),
                  (1, -2), (2, -1), (-1, -2), (-2, -1)]


class Pawn(Piece):

    _enpassant_squares = {
        common.WHITE: 4,
        common.BLACK: 3
    }

    @classmethod
    def move_iterators(*args, **kwargs):
        return []

    @common.listify
    @provide_position
    def _get_special_threatened_moves(self, position, chess_board):
        new_rank_index = position.rank_index + self.color
        for new_file_index in (-1 + position.file_index, 1 + position.file_index):
            new_position = common.Position(new_rank_index, new_file_index)
            if (chess_board[new_position].color == self.color * -1 or
                self.is_enpassant_available(position, new_position, chess_board)):
                yield new_position
        new_position = position.replace(new_rank_index)
        if chess_board[new_position].color == common.NONE:
            yield new_position

        # Check for double pawn move.
        if position.rank_index == _back_rank_squares[self.color] + self.color:
            new_position = position.replace(self.color * 2)
            if chess_board[new_position].color == common.NONE:
                yield new_position

    @property
    def enpassant_square(self):
        return self._enpassant_squares[self.color]

    def is_enpassant_available(self, position, new_position, chess_board):
        if position.rank_index != self.enpassant_square:
            return False

        last_move = chess_board.moves[-1]
        if not last_move:
            return False

        return (type(last_move.piece) == type(self) and
                last_move.source_file == new_position.file_index and
                last_move.source_rank == new_position.rank_index + self.color and
                last_move.dest_rank == new_position.rank_index - self.color)

    def build_disambiguation(self, chess_board, move):
        return "" if move.source_file == move.dest_file else \
            common.file_index_to_file_letter(move.source_file)