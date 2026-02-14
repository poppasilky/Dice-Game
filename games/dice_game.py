def new_game():
    return {
        'turn': 1,
        'point': None,
        'game_over': False,
        'message': ''
    }

def process_roll(game, roll):
    if game['game_over']:
        game['message'] = 'Game over. Start a new game.'
        return game

    if game['turn'] == 1:
        if roll in [7, 11]:
            game['game_over'] = True
            game['message'] = f'You rolled {roll} – You win!'
        elif roll in [2, 3, 12]:
            game['game_over'] = True
            game['message'] = f'You rolled {roll} – You lose!'
        else:
            game['point'] = roll
            game['turn'] = 2
            game['message'] = f'You rolled {roll} – Point set to {roll}. Turn 2'
    else:
        if roll == game['point']:
            game['game_over'] = True
            game['message'] = f'You rolled {roll} – You win!'
        elif roll == 7:
            game['game_over'] = True
            game['message'] = f'You rolled {roll} – You lose!'
        else:
            game['turn'] += 1
            game['message'] = f'You rolled {roll} – No win/loss. Turn {game["turn"]}'

    return game