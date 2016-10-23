import itertools
from app import api_set_routes
from tests.test_resources import BaseTest


class BaseIntegrationTest(BaseTest):
    def setUp(self):
        super(BaseIntegrationTest, self).setUp()
        api_set_routes(self.api)


class TestOneTurn(BaseIntegrationTest):
    paths = {
        'board': '/board',
        'new_game': '/new_game',
        'start_turn': '/start_turn',
        'vote': '/vote',
        'compute_votes': '/compute_votes',
    }

    test_word1 = 'Igreja'
    test_word2 = 'Tanque'

    vote_data = [
        {'user': 'a', 'word': test_word1},
        {'user': 'b', 'word': test_word1},
        {'user': 'c', 'word': test_word1},
        {'user': 'd', 'word': test_word2},
        {'user': 'e', 'word': test_word2},
    ]

    def new_game(self):
        self.simulate_get(self.paths['new_game'])

    def start_turn(self):
        self.simulate_get(self.paths['start_turn'])

    def compute_votes(self):
        self.simulate_get(self.paths['compute_votes'])

    def vote(self, vote):
        self.simulate_post(self.paths['vote'], body=vote)

    def get_board(self):
        response = self.simulate_get(self.paths['board'])
        return self.body_as_json(response)

    def get_word(self, word, words):
        _word = list(filter(
            lambda x: x['word'] == word, words))
        return _word[0] if _word else None

    def test_a_single_game_turn(self):
        """ A single turn should work """
        self.new_game()
        self.start_turn()
        for v in self.vote_data:
            self.vote(v)

        # should start with red team
        body = self.get_board()
        self.assertEqual(body['turn'], 'red')

        # should turn public the most voted word aligment
        self.compute_votes()
        body = self.get_board()
        most_voted_word = self.get_word(self.test_word1, body['words'])
        self.assertEqual(most_voted_word['public'], True)

        # should change the turn after the vote computing
        self.assertEqual(body['turn'], 'blue')

    def test_multiples_votes_from_single_user(self):
        """ Multiples votes from a single user """
        self.new_game()
        self.start_turn()
        votes = [
            {'user': 'A', 'word': 'Igreja'},
            {'user': 'A', 'word': 'Tanque'},
        ]
        for v in votes:
            self.vote(v)

        body = self.get_board()
        self.assertEqual(len(body['votes']), 1)
        self.assertEqual(body['votes']['A'], 'Tanque')

    def test_user_can_skip_choosing_a_word(self):
        """ If most users vote blank the turn should be skipped """
        self.new_game()
        self.start_turn()

        blank_votes = [
            {'user': 'A' + str(i), 'word': ''}
            for i in range(1, 3)]
        votes = [
            {'user': 'B' + str(i), 'word': self.test_word2}
            for i in range(1, 3)]
        for v in itertools.chain(blank_votes, votes):
            self.vote(v)

        # the turn start with red team
        body = self.get_board()
        self.assertEqual(body['turn'], 'red')

        self.compute_votes()
        body = self.get_board()

        # after computing the votes no word should be public and the turn
        # should be changed to blue team
        public_words = list(
            filter(lambda x: x['public'] is True, body['words']))
        self.assertEqual(public_words, [])
        self.assertEqual(body['turn'], 'blue')
