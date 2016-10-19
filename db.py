from collections import Counter
from datetime import datetime, timedelta
from pymongo import MongoClient


class SaigonConnector:

    def __init__(self):
        self.client = MongoClient('localhost', 27017)

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

    def retrieve_one(self, id=None):
        query = {}
        if id:
            query['_id'] = id

        return self.collection.find_one(query)

    def replace(self, obj, id=None):
        query = {}
        if id:
            query['_id'] = id

        return self.collection.replace_one(query, obj)


class GameRepository(BaseRepository):
    collection_name = 'games'

    def count(self):
        return self.collection.count()

    def new(self, start_team, words):
        # remove o jogo antigo
        self.delete()

        words = WordRepository().bulk_new(words)

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

        voting_expires_at = game.get('voting_expires_at')
        if voting_expires_at and voting_expires_at < datetime.now():
            self.count_votes(game['votes'])
            #####

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

        if counter[''] > total_votes // 2:
            self.end_turn()
        else:

            word, votes = counter.most_common()[0]

            WordRepository().publish_word(word)


class WordRepository(BaseRepository):
    collection_name = 'words'

    def all(self):
        return [word for word in self.collection.find()]

    def bulk_new(self, words):
        result = self.collection.insert_many(self.proccess_words(words))
        return self.all()

    def proccess_words(self, words):
        return [
            {
                'word': word['word'],
                'alignment': word['alignment'],
                'public_alignment': None
            }
            for word in words
        ]

    def publish_word(self, word):
        word = self.retrieve_one(word=word)
        word = self.collection.find_one({'_id': obj_id})
        word['public_alignment'] = word['alignment']

        self.replace(word, id=obj_id)


