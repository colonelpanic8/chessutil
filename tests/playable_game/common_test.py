import testify as T

from playable_game import common


class CommonTestCase(T.TestCase):

    def test_parse_long_uci_string(self):
        T.assert_equal(
            common.parse_long_uci_string('e4e5a6a7b3b5e7e8qd7d8rd3d4'),
            ['e4e5', 'a6a7', 'b3b5', 'e7e8q', 'd7d8r', 'd3d4']
        )


if __name__ == '__main__':
    T.run()