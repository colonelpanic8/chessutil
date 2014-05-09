from . import *


class ClearBoardChessRulesTestCase(ClearedBoardPlayableChessGameTestCase):

    def make_legal_promotion(self, src, dst, **kwargs):
        return self.make_legal_move(Move(src, dst, self.chess_rules, **kwargs))

    def test_en_passant(self):
        self.chess_board[6, 0] = pieces.Pawn(common.color.BLACK)
        self.chess_board[4, 1] = pieces.Pawn(common.color.WHITE)
        self.chess_rules.action = common.color.BLACK
        self.make_legal_moves([((6, 0), (4, 0)), ((4, 1), (5, 0))])
        T.assert_equal(self.chess_board[4, 0].is_empty, True)
        T.assert_equal(self.chess_board[5, 0], pieces.Pawn(common.color.WHITE))

        self.chess_board[1, 6] = pieces.Pawn(common.color.WHITE)
        self.chess_board[3, 7] = pieces.Pawn(common.color.BLACK)
        self.chess_rules.action = common.color.WHITE
        self.make_legal_moves([((1, 6), (3, 6)), ((3, 7), (2, 6))])
        T.assert_equal(self.chess_board[3, 6].is_empty, True)
        T.assert_equal(self.chess_board[2, 6], pieces.Pawn(common.color.BLACK))

    def test_basic_promotion(self):
        self.make_legal_moves([((0, 4), (1, 4)), ((7, 4), (6, 4))])
        self.chess_board[6, 0] = pieces.Pawn(common.color.WHITE)
        self.chess_board[1, 0] = pieces.Pawn(common.color.BLACK)

        T.assert_raises(common.IllegalMoveError, self.make_legal_move,
                        ((6, 0), (7, 0)))
        self.make_legal_promotion((6, 0), (7, 0),
                        promotion=pieces.Queen)
        T.assert_equal(self.chess_board[7, 0], pieces.Queen(common.color.WHITE))

        self.make_legal_promotion((1, 0), (0, 0),
                                  promotion=pieces.Queen)
        T.assert_equal(self.chess_board[0, 0], pieces.Queen(common.color.BLACK))

    def test_queenside_castling_and_castling_through_check(self):
        self.chess_board[0, 0] = pieces.Rook(common.color.WHITE)
        self.chess_board[7, 0] = pieces.Rook(common.color.BLACK)
        self.make_legal_move(((0, 4), (0, 2)))
        T.assert_equal(self.chess_board[0, 2], pieces.King(common.color.WHITE))
        T.assert_equal(self.chess_board[0, 3], pieces.Rook(common.color.WHITE))
        T.assert_equal(self.chess_board[0, 4], pieces.Empty)
        T.assert_equal(self.chess_board[0, 0], pieces.Empty)

        # This should raise because the rook blocks the castling of the black king
        T.assert_raises(
            common.IllegalMoveError,
            self.make_legal_move,
            ((7, 4), (7, 2))
        )
        self.chess_board[0, 3] = pieces.Empty
        self.make_legal_move(((7, 4), (7, 2)))
        T.assert_equal(self.chess_board[7, 2], pieces.King(common.color.BLACK))
        T.assert_equal(self.chess_board[7, 3], pieces.Rook(common.color.BLACK))


class DefaultBoardChessRulesTestCase(BasePlayableChessGameTestCase):

    moves_for_castling = [
        ((1, 4), (3, 4)),
        ((6, 4), (4, 4)),
        ((0, 6), (2, 5)),
        ((7, 6), (5, 5)),
        ((0, 5), (1, 4)),
        ((7, 5), (6, 4)),
    ]

    def test_kingside_castling_fails_when_rook_moves_back_into_position(self):
        self.make_legal_moves(self.moves_for_castling)
        self.make_legal_moves([
            ((0, 7), (0, 6)),
            ((7, 7), (7, 6)),
            ((0, 6), (0, 7)),
            ((7, 6), (7, 7))
        ])

        T.assert_raises(
            common.IllegalMoveError,
            self.make_legal_move,
            ((0, 4), (0, 6))
        )

        self.make_legal_move(((0, 4), (0, 5)))

        T.assert_raises(
            common.IllegalMoveError,
            self.make_legal_move,
            ((7, 4), (7, 6))
        )

    def test_kingside_castling_and_castling_while_in_check(self):
        for move_num, move in enumerate(self.moves_for_castling):
            back_rank = move_num % 2 * 7
            assert (back_rank, 6) not in self.chess_rules.get_legal_moves(((back_rank, 4)))
            self.make_legal_move(move)

        self.make_legal_move((0, 4), (0, 6))
        T.assert_equal(self.chess_board[0, 6], pieces.King(common.color.WHITE))
        T.assert_equal(self.chess_board[0, 5], pieces.Rook(common.color.WHITE))
        T.assert_equal(self.chess_board[0, 4], pieces.Empty)
        T.assert_equal(self.chess_board[0, 7], pieces.Empty)

        self.chess_board[6, 4] = pieces.Rook(common.color.WHITE)
        T.assert_raises(common.IllegalMoveError, self.make_legal_move,
                        ('e8', 'g8'))
        self.chess_board[6, 4] = pieces.Empty
        self.make_legal_move((7, 4), (7, 6))
        T.assert_equal(self.chess_board[7, 6], pieces.King(common.color.BLACK))
        T.assert_equal(self.chess_board[7, 5], pieces.Rook(common.color.BLACK))

    def test_get_item_of_chess_board(self):
        T.assert_equal(self.chess_board[0, 0], pieces.Rook(common.color.WHITE))

    def test_get_legal_moves_with_queen_and_double_check(self):
        self.chess_board[1, 4] = pieces.Queen(common.color.WHITE)
        self.chess_board[2, 5] = pieces.Pawn(common.color.BLACK)
        self.chess_board[5, 0] = pieces.Bishop(common.color.WHITE)
        #   +-----------------+
        # 8 | R N B Q K B N R |
        # 7 | P P P P P P P P |
        # 6 | b . . . . . . . |
        # 5 | . . . . . . . . |
        # 4 | . . . . . . . . |
        # 3 | . . . . . P . . |
        # 2 | p p p p q . p p |
        # 1 | r n b q k b n r |
        #   +-----------------+
        #     A B C D E F G H

        all_moves = set()
        # All the straight moves.
        all_moves.update([(i, 4) for i in range (2, 7)])
        # Should be able to take the blocking pawn.
        all_moves.add((2, 5))
        # Up to the blocking bishop.
        all_moves.update([(1 + i, 4 - i) for i in range(1,4)])
        self.assert_position_sets_equal(
            set(self.chess_rules.get_legal_moves('e2')),
            set(map(Position.make, all_moves))
        )
        self.chess_board[1, 5] = pieces.Empty

        all_moves.add((1, 5))

        self.assert_position_sets_equal(
            set(self.chess_rules.get_legal_moves((1, 4))),
            set(map(Position.make, all_moves))
        )

        # The only available moves should be on the current file.
        #   +-----------------+
        # 8 | R N B Q K B N R |
        # 7 | P P P P P P P P |
        # 6 | b . . . . . . . |
        # 5 | . . . . R . . . |
        # 4 | . . . . . . . . |
        # 3 | . . . . . P . . |
        # 2 | p p p p q . p p |
        # 1 | r n b q k b n r |
        #   +-----------------+
        #     A B C D E F G H

        self.chess_board[4, 4] = pieces.Rook(common.color.BLACK)
        self.assert_position_sets_equal(
            set(self.chess_rules.get_legal_moves((1, 4))),
            set([Position.from_rank_file(i, 4) for i in range(2, 5)])
        )

        # There should be no available moves because of the double check.
        self.chess_board.set_piece((1, 5), pieces.Bishop(common.color.BLACK))
        self.assert_position_sets_equal(set(self.chess_rules.get_legal_moves('e2')), set())

        # The king has to take.
        self.assert_position_sets_equal(set(self.chess_rules.get_legal_moves('e1')), set([Position.make('f2')]))

    def test_get_legal_moves_for_rook_with_capture(self):
        self.chess_board[1, 0] = pieces.Empty
        self.assert_position_sets_equal(
            self.chess_rules.get_legal_moves((0, 0)),
            [(i, 0) for i in range (1, 7)]
        )

    def test_get_legal_moves_for_rook_without_capture(self):
        self.chess_rules.make_legal_move(self.build_move((1, 0), (3, 0)))
        self.chess_rules.make_legal_move(self.build_move((6, 0), (4, 0)))
        self.assert_position_sets_equal(
            set(self.chess_rules.get_legal_moves((0, 0))),
            set([(i, 0) for i in range (1, 3)])
        )
        self.assert_position_sets_equal(self.chess_rules.get_legal_moves((3, 0)), [])
        self.chess_rules.make_legal_move(self.build_move((1, 1), (3, 1)))
        self.assert_position_sets_equal(self.chess_rules.get_legal_moves((4, 0)), set([(3, 1)]))

    def test_double_pawn_move(self):
        self.make_legal_move((1, 3), (3, 3))
        self.make_legal_move((6, 3), (4, 3))
        T.assert_equal(self.chess_board[3, 3], pieces.Pawn(common.color.WHITE))
        T.assert_equal(self.chess_board[4, 3], pieces.Pawn(common.color.BLACK))

        self.chess_board[3, 7] = pieces.Pawn(common.color.BLACK)
        T.assert_raises(
            common.IllegalMoveError,
            self.make_legal_move,
            (1, 7), (3, 7)
        )

        self.chess_board[2, 6] = pieces.Pawn(common.color.WHITE)
        T.assert_raises(
            common.IllegalMoveError,
            self.make_legal_move,
            (1, 6), (3, 6)
        )

    def test_active_color_error(self):
        T.assert_raises(
            common.ActiveColorError,
            self.chess_rules.get_legal_moves,
            (7, 0)
        )

        self.chess_rules.make_legal_move(self.build_move((1, 0), (3, 0)))

        T.assert_raises(
            common.ActiveColorError,
            self.chess_rules.get_legal_moves,
            (0, 0)
        )


if __name__ == '__main__':
    T.run()
