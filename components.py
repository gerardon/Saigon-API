from collections import Counter
from fixtures import board, public_board


class Board(object):

    def __init__(self):
        self._board = board
        self.public_board = public_board
        self.start_team = self._initial_turn()
        self.words = [x['word'] for x in self.public_board]

    def _initial_turn(self):
        counter = Counter([b['alignment'] for b in self._board])
        return counter.most_common()[0][0]
