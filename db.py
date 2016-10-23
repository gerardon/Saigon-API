import json
import datetime
from bson import ObjectId
from collections import Counter
from datetime import datetime, timedelta
from pymongo import MongoClient


class SaigonConnector:

    def __init__(self):
        self.client = MongoClient('localhost', 27017, socketKeepAlive=True)

    @property
    def database(self):
        return self.client['saigon']

    def dropdb(self):
        for collection in self.database.collection_names(include_system_collections=False):
            self.database.drop_collection(collection)


class BaseRepository:
    collection_name = None

    def __init__(self):
        self.connector = SaigonConnector()

    @property
    def collection(self):
        return self.connector.database[self.collection_name]

    def retrieve_one(self, id=None, extra_qs={}):
        if id:
            extra_qs['_id'] = id

        return self.collection.find_one(extra_qs)

    def replace(self, obj, id=None):
        query = {}
        if id:
            query['_id'] = id

        return self.collection.replace_one(query, obj)

    def count(self):
        return self.collection.count()


class GameRepository(BaseRepository):
    collection_name = 'games'

    @classmethod
    def get_start_team(cls, words):
        counter = Counter([b['alignment'] for b in words])
        return counter.most_common()[0][0]

    def new(self, start_team, words):
        # remove o jogo antigo
        self.delete()

        wr = WordRepository()
        wr.collection.delete_many({})
        words = wr.bulk_new(words)

        result = self.collection.insert_one(
            {
                'turn': start_team,
                'voting_expires_at': None,
                'votes': {},
                'words': words
            }
        )
        return self.retrieve_one(result.inserted_id)

    def delete(self):
        return self.collection.delete_one({})

    def retrieve_one(self, *args, **kwargs):
        game = super(GameRepository, self).retrieve_one(*args, **kwargs)

        if game:
            voting_expires_at = game.get('voting_expires_at')
            if voting_expires_at and voting_expires_at < datetime.now():
                self.count_votes(game['votes'])

        return game

    def end_turn(self):
        game = self.retrieve_one()
        game['turn'] = 'blue' if game['turn'] == 'red' else 'red'
        self.replace(game)

    def start_voting(self):
        game = self.retrieve_one()
        game['voting_expires_at'] = datetime.now() + timedelta(minutes=2)
        self.replace(game)

    def vote(self, user_uuid, word):
        game = self.retrieve_one()
        game['votes'][str(user_uuid)] = word
        self.replace(game)

    def count_votes(self, votes):
        votes = votes.values()
        total_votes = len(votes)
        counter = Counter(votes)

        if not counter:
            return

        if counter[''] > total_votes // 2:
            self.end_turn()
        else:
            word, votes = counter.most_common()[0]

            word_repository = WordRepository()
            word_repository.publish_word(word)
            words = word_repository.all()
            game = self.retrieve_one()
            game['words'] = words
            self.replace(game)

    def compute_votes(self, game=None):
        game = self.retrieve_one(game or {})
        if not game:
            return

        self.count_votes(game['votes'])
        self.end_turn()


class WordRepository(BaseRepository):
    collection_name = 'words'

    def retrieve_one(self, word=None, *args, **kwargs):
        extra_qs = {}
        if word:
            extra_qs['word'] = word

        return super(WordRepository, self).retrieve_one(*args, extra_qs=extra_qs, **kwargs)

    def all(self):
        return [word for word in self.collection.find()]

    def new(self, word, alignment):
        result = self.collection.insert_one(self.proccess_word(word, alignment))
        return self.retrieve_one(id=result.inserted_id)

    def bulk_new(self, words):
        words = [self.proccess_word(w['word'], w['alignment']) for w in words]
        result = self.collection.insert_many(words)
        return self.all()

    def proccess_word(self, word, alignment):
        return {
            'word': word,
            'alignment': alignment,
            'public': False,
        }

    def publish_word(self, word):
        word = self.collection.update_one({'word': word}, {'$set': {'public': True}})


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def json_encode(value):
    return JSONEncoder().encode(value)
