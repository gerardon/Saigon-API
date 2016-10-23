import json
import urllib
from falcon.testing import TestCase
from resources import (BoardResource, StartTurnResource, VoteResource,
                       ComputeVotesResource)
from fixtures import load_game
from app import api_setup


class BaseTest(TestCase):
    path = None
    resource = None

    def setUp(self):
        super(BaseTest, self).setUp()
        if self.path and self.resource:
            self.api.add_route(self.path, self.resource())
        api_setup(self.api)

    def simulate_post(self, path, body):
        body = urllib.parse.urlencode(body)
        return super(BaseTest, self).simulate_post(
            path, body=body,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def body_as_json(self, response):
        return json.loads(response.content.decode('utf-8'))


class TestBoardResource(BaseTest):
    path = '/board'
    resource = BoardResource

    def test_board_should_return_200(self):
        response = self.simulate_get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_board_should_have_expected_info(self):
        load_game()
        response = self.simulate_get(self.path)
        body = self.body_as_json(response)
        assert('words' in body.keys())
        self.assertEqual(type(body.get('words', None)), list)


class TestTurnResource(BaseTest):
    path = '/turn'
    resource = StartTurnResource

    def test_turn_should_return_200(self):
        response = self.simulate_get(self.path)
        self.assertEqual(response.status_code, 302)


class TestVote(BaseTest):
    path = '/vote'
    resource = VoteResource

    def test_vote_should_return_302(self):
        response = self.simulate_post(
            self.path, body={'user': 'A', 'word': 'Igreja'})
        self.assertEqual(response.status_code, 302)


class TestComputeVotesResource(BaseTest):
    path = '/compute_votes'
    resource = ComputeVotesResource

    def test_vote_should_return_302(self):
        response = self.simulate_get(self.path)
        self.assertEqual(response.status_code, 302)
