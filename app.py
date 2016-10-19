import falcon
import json
import urllib

from fixtures import public_board as board, status


class BaseResource(object):
    def format(self, value):
        return json.dumps(value)

    def set_body(self, resp, value):
        resp.body = self.format(value)

    def parse_post(self, req):
        content = req.stream.read().decode('utf-8')
        return dict(urllib.parse.parse_qsl(content))

    def set_error(self, resp, error_message):
        error = {'level': 'ERROR', 'message': error_message}
        resp.status = falcon.HTTP_500
        self.set_body(resp, error)

    def get_url(self, req, path):
        parsed_url = urllib.parse.urlparse(req.url)
        return '{uri.scheme}://{uri.netloc}/{path}'.format(
            uri=parsed_url, path=path)

    def validate(self, resp, data):
        return True


class BoardResource(BaseResource):
    def on_get(self, req, resp):
        self.set_body(
            resp, {'board': board, 'info': status})


class TurnResource(BaseResource):
    def on_post(self, req, resp):
        data = self.parse_post(req)
        if not self.validate(resp, data):
            return

        raise falcon.HTTPFound(self.get_url(req, 'board'))

    def validate(self, resp, data):
        if not data.get('status'):
            self.set_error(resp, 'You should send a "status" parameter')
            return False

        if data['status'] not in ['start', 'stop']:
            self.set_error(resp, 'The value of status parameter should '
                                 'be either start or stop')
            return False

        return True


class VoteResource(BaseResource):
    def on_post(self, req, resp):
        data = self.parse_post(req)
        if not self.validate(resp, data):
            return

        raise falcon.HTTPFound(self.get_url(req, 'board'))

    def validate(self, resp, data):
        if not data.get('word'):
            self.set_error(resp, 'You should send a "word" parameter')
            return False
        return True

api = falcon.API()
api.add_route('/board', BoardResource())
api.add_route('/turn', TurnResource())
api.add_route('/vote', VoteResource())
