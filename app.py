import falcon
import json

from fixtures import public_board as board, status


class BaseResource(object):
    def format(self, value):
        return json.dumps(value)

    def set_body(self, resp, value):
        resp.body = self.format(value)


class BoardResource(BaseResource):
    def on_get(self, req, resp):
        self.set_body(
            resp, {'board': board, 'info': status})

class TurnResource(BaseResource):
    def on_get(self, req, resp):
        pass

api = falcon.API()
api.add_route('/board', BoardResource())
