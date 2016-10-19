import json
import urllib
from falcon.testing import TestCase
from resources import BoardResource, StartTurnResource


class BaseTest(TestCase):
    path = None
    resource = None

    def setUp(self):
        super(BaseTest, self).setUp()
        self.api.add_route(self.path, self.resource())

    def format_post_data(self, values_dict):
        return urllib.parse.urlencode(values_dict)


class TestBoardResource(BaseTest):
    path = '/board'
    resource = BoardResource

    def test_board_should_return_200(self):
        response = self.simulate_get(self.path)
        self.assertEqual(response.status_code, 200)

    def test_board_should_have_expected_info(self):
        response = self.simulate_get(self.path)
        body = json.loads(response.content.decode('utf-8'))
        assert('board' in body.keys())
        assert('info' in body.keys())
        self.assertEqual(type(body.get('board')), list)


class TestTurnResource(BaseTest):
    path = '/turn'
    resource = StartTurnResource

    def test_turn_should_return_200(self):
        response = self.simulate_get(self.path)
        self.assertEqual(response.status_code, 302)
