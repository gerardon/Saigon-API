import falcon
import urllib

from db import GameRepository, json_encode
from fixtures import board


class BaseResource(object):
    def format(self, value):
        return json_encode(value)

    def set_body(self, resp, value):
        resp.body = self.format(value)

    def set_error(self, resp, error_message):
        error = {'level': 'ERROR', 'message': error_message}
        resp.status = falcon.HTTP_500
        self.set_body(resp, error)

    def get_url(self, req, path):
        parsed_url = urllib.parse.urlparse(req.url)
        return '{uri.scheme}://{uri.netloc}/{path}'.format(
            uri=parsed_url, path=path)

    def validate(self, req, resp):
        return True


class BoardResource(BaseResource):
    def on_get(self, req, resp):
        gr = GameRepository()
        self.set_body(resp, gr.retrieve_one())


class NewGameResource(BaseResource):
    def on_get(self, req, resp):
        gr = GameRepository()
        start_team = GameRepository.get_start_team(board)
        self.set_body(resp, gr.new(start_team, board))


class StartTurnResource(BaseResource):
    def on_get(self, req, resp):
        gr = GameRepository()
        gr.start_voting()
        raise falcon.HTTPFound(self.get_url(req, 'board'))


class VoteResource(BaseResource):
    def on_post(self, req, resp):
        if not self.validate(req, resp):
            return
        gr = GameRepository()
        gr.vote(req.params['user'], req.params['word'])
        raise falcon.HTTPFound(self.get_url(req, 'board'))

    def validate(self, req, resp):
        if not req.params.get('word'):
            req.params['word'] = ''

        if not req.params.get('user'):
            self.set_error(resp, 'You should send a "user" parameter')
            return False

        return True


class ComputeVotesResource(BaseResource):
    def on_get(self, req, resp):
        gr = GameRepository()
        gr.compute_votes()
        raise falcon.HTTPFound(self.get_url(req, 'board'))


class WinnerResource(BaseResource):
    def on_get(self, req, resp):
        gr = GameRepository()
        winner = gr.who_is_the_winner() or ''
        self.set_body(resp, {'winner': winner})
