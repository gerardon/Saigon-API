import falcon
from resources import (BoardResource, StartTurnResource, VoteResource,
                       NewGameResource)


api = falcon.API()
api.req_options.auto_parse_form_urlencoded = True
api.add_route('/board', BoardResource())
api.add_route('/start_turn', StartTurnResource())
api.add_route('/vote', VoteResource())
api.add_route('/new_game', NewGameResource())
