import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from uuid import uuid4

from db import SaigonConnector, GameRepository, WordRepository


class PyMongoTestCase(unittest.TestCase):

    def tearDown(self):
        SaigonConnector().dropdb()


class GameRepositoryTestCase(PyMongoTestCase):
    def setUp(self):
        self.repository = GameRepository()

    def start_game_fixture(self):
        def build_word(i, alignment):
            return {
                'word': '{}_word_{}'.format(alignment, i),
                'alignment': alignment,
            }

        words = [build_word(i, 'red') for i in range(9)]
        words.extend([build_word(i, 'blue') for i in range(8)])
        words.extend([build_word(i, 'civil') for i in range(7)])
        words.extend([build_word(i, 'killer') for i in range(1)])
        return self.repository.new(start_team='red', words=words)

    def test_start_mongo_client_at_init(self):
        self.assertIsInstance(self.repository.connector, SaigonConnector)

    def test_count_should_call_collection_count(self):
        self.assertEqual(GameRepository().count(), 0)

    @patch.object(WordRepository, 'bulk_new')
    def test_new_creates_a_new_game(self, bulk_patched):
        bulk_patched.return_value = []
        self.assertEqual(self.repository.count(), 0)

        self.repository.new(start_team='red', words=[])

        bulk_patched.assert_called_once_with([])

        self.assertEqual(self.repository.count(), 1)

        game = self.repository.retrieve_one()
        self.assertEqual(game['turn'], 'red')
        self.assertEqual(game['words'], [])

    def test_delete_deletes_the_game(self):
        self.start_game_fixture()

        self.assertEqual(self.repository.count(), 1)
        self.repository.delete()
        self.assertEqual(self.repository.count(), 0)

    @patch.object(WordRepository, 'bulk_new', Mock(return_value=[]))
    def test_new_deletes_previous_game(self):
        game = self.repository.new(start_team='red', words=[])
        self.assertEqual(self.repository.count(), 1)

        game = self.repository.new(start_team='blue', words=[])
        self.assertEqual(self.repository.count(), 1)

    def test_start_voting(self):
        game = self.start_game_fixture()

        self.assertIsNone(game['voting_expires_at'])

        self.repository.start_voting()
        game = self.repository.retrieve_one()

        self.assertIsInstance(game['voting_expires_at'], datetime)

    def test_vote_should_add_a_vote_to_game(self):
        game = self.start_game_fixture()

        self.repository.vote('uuid', 'gancho')

        game = self.repository.retrieve_one()
        self.assertIn('uuid', game['votes'])
        self.assertEqual(game['votes']['uuid'], 'gancho')

    @patch.object(WordRepository, 'publish_word')
    def test_count_votes_should_publish_the_winner(self, mocked_publish):
        self.start_game_fixture()
        self.repository.vote(uuid4(), 'red_word_0')
        self.repository.vote(uuid4(), 'red_word_0')
        self.repository.vote(uuid4(), 'red_word_1')

        game = self.repository.retrieve_one()

        self.repository.count_votes(game['votes'])

        mocked_publish.assert_called_once_with('red_word_0')

    @patch.object(GameRepository, 'end_turn')
    def test_count_votes_should_end_the_turn_if_more_empty_votes(self, end_mocked):
        self.start_game_fixture()
        self.repository.vote(uuid4(), '')
        self.repository.vote(uuid4(), '')
        self.repository.vote(uuid4(), 'red_word_0')

        game = self.repository.retrieve_one()

        self.repository.count_votes(game['votes'])
        end_mocked.assert_called_once_with()

    def test_end_turn_should_toggle_the_turn(self):
        self.start_game_fixture()
        game = self.repository.retrieve_one()

        self.assertEqual(game['turn'], 'red')
        self.repository.end_turn()

        game = self.repository.retrieve_one()
        self.assertEqual(game['turn'], 'blue')


class WordRepositoryTestCase(PyMongoTestCase):
    def setUp(self):
        self.repository = WordRepository()

    def test_bulk_new_should_insert_word_list_and_return_docs(self):
        word_docs = self.repository.bulk_new([
            {'word': 'word_{}'.format(i), 'alignment': 'red'}
            for i in range(5)
        ])

        self.assertEqual(self.repository.count(), 5)

        for word in word_docs:
            self.assertIn('_id', word)

    def test_all_returns_a_word_list(self):
        self.repository.bulk_new([
            {'word': 'word_{}'.format(i), 'alignment': 'red'}
            for i in range(5)
        ])

        self.assertIsInstance(self.repository.all(), list)

    @patch.object(WordRepository, 'proccess_word')
    def test_new_calls_proccess_words_and_inserts(self, patched_proccess):
        patched_proccess.return_value = {'galinha': True}

        word = self.repository.new('soueto', 'red')

        self.assertIn('galinha', word)
        self.assertIn('_id', word)
        self.assertTrue(word['galinha'])


    def test_publish_word_makes_its_alignment_public(self):
        word = self.repository.new('soueto', 'red')
        self.assertFalse(word['public'])

        self.repository.publish_word('soueto')

        word = self.repository.retrieve_one(word='soueto')
        self.assertTrue(word['public'])

