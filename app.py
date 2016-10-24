import falcon
from resources import (BoardResource, StartTurnResource, VoteResource,
                       NewGameResource, ComputeVotesResource, WinnerResource)


def api_setup(api):
    api.req_options.auto_parse_form_urlencoded = True
    return api


def api_set_routes(api):
    api.add_route('/board', BoardResource())
    api.add_route('/start_turn', StartTurnResource())
    api.add_route('/vote', VoteResource())
    api.add_route('/new_game', NewGameResource())
    api.add_route('/compute_votes', ComputeVotesResource())
    api.add_route('/who_is_the_winner', WinnerResource())
    return api

api = api_setup(falcon.API())
api = api_set_routes(api)
