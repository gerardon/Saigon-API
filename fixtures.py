RED_TEAM = 'red'
BLUE_TEAM = 'blue'
CIVIL = 'civil'
KILLER = 'killer'

board = [
    {'word': 'Fonte', 'alignment': RED_TEAM},
    {'word': 'Concerto', 'alignment': RED_TEAM},
    {'word': 'Fichário', 'alignment': RED_TEAM},
    {'word': 'Círculo', 'alignment': RED_TEAM},
    {'word': 'América', 'alignment': RED_TEAM},
    {'word': 'Curso', 'alignment': RED_TEAM},
    {'word': 'Tomada', 'alignment': RED_TEAM},
    {'word': 'Escorpião', 'alignment': RED_TEAM},
    {'word': 'Alienígena', 'alignment': RED_TEAM},

    {'word': 'Espaço', 'alignment': BLUE_TEAM},
    {'word': 'Fio', 'alignment': BLUE_TEAM},
    {'word': 'Presunto', 'alignment': BLUE_TEAM},
    {'word': 'Data', 'alignment': BLUE_TEAM},
    {'word': 'Flauta', 'alignment': BLUE_TEAM},
    {'word': 'Aranha', 'alignment': BLUE_TEAM},
    {'word': 'Espinha', 'alignment': BLUE_TEAM},
    {'word': 'Dose', 'alignment': BLUE_TEAM},

    {'word': 'Coberta', 'alignment': CIVIL},
    {'word': 'Buzina', 'alignment': CIVIL},
    {'word': 'Rainha', 'alignment': CIVIL},
    {'word': 'Ligação', 'alignment': CIVIL},
    {'word': 'Igreja', 'alignment': CIVIL},
    {'word': 'Tanque', 'alignment': CIVIL},
    {'word': 'Atlântida', 'alignment': CIVIL},

    {'word': 'Dragão', 'alignment': KILLER},
]

public_board = [
    {'word': 'Fonte', 'alignment': None},
    {'word': 'Concerto', 'alignment': None},
    {'word': 'Fichário', 'alignment': None},
    {'word': 'Círculo', 'alignment': None},
    {'word': 'América', 'alignment': None},
    {'word': 'Curso', 'alignment': None},
    {'word': 'Tomada', 'alignment': None},
    {'word': 'Escorpião', 'alignment': None},
    {'word': 'Alienígena', 'alignment': None},
    {'word': 'Espaço', 'alignment': None},
    {'word': 'Fio', 'alignment': None},
    {'word': 'Presunto', 'alignment': None},
    {'word': 'Data', 'alignment': None},
    {'word': 'Flauta', 'alignment': None},
    {'word': 'Aranha', 'alignment': None},
    {'word': 'Espinha', 'alignment': None},
    {'word': 'Dose', 'alignment': None},
    {'word': 'Coberta', 'alignment': None},
    {'word': 'Buzina', 'alignment': None},
    {'word': 'Rainha', 'alignment': None},
    {'word': 'Ligação', 'alignment': None},
    {'word': 'Igreja', 'alignment': None},
    {'word': 'Tanque', 'alignment': None},
    {'word': 'Atlântida', 'alignment': None},
    {'word': 'Dragão', 'alignment': None},
]


def load_game():
    from db import GameRepository
    start_team = GameRepository.get_start_team(board)
    gr = GameRepository()
    gr.new(start_team, board)


def set_winner(game, team):
    from db import GameRepository, WordRepository
    wr = WordRepository()
    gr = GameRepository()
    wr.collection.update_many({'alignment': team}, {'$set': {'public': True}})
    game = gr.retrieve_one(game)
    game['words'] = wr.all()
    gr.replace(game)
