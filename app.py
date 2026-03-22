from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'your-secret-key'

def new_game(mode='pig_single'):
    return {
        'mode': mode,
        'player_score': 0,
        'ghost_score': 0,
        'ghost_round_points': 0,          # added: ghost's current turn points
        'player_dice1': 0,
        'player_dice2': 0,
        'ghost_dice1': 0,
        'ghost_dice2': 0,
        'turn': 'player',
        'round_points': 0,                # player's turn points
        'game_over': False,
        'message': 'Roll the dice!',
        'point': None if mode == 'craps' else None,
        'come_out': True if mode == 'craps' else None
    }

def roll_dice():
    return random.randint(1, 6)

def player_roll(state):
    if state['game_over'] or state['turn'] != 'player':
        return state

    mode = state['mode']
    if mode == 'pig_single':
        roll = roll_dice()
        state['player_dice1'] = roll
        if roll == 1:
            state['round_points'] = 0
            state['turn'] = 'ghost'
            state['message'] = 'You rolled a 1! No points. Ghost\'s turn.'
        else:
            state['round_points'] += roll
            state['message'] = f'You rolled {roll}. Turn: {state["round_points"]} points.'

    elif mode == 'pig_two':
        d1, d2 = roll_dice(), roll_dice()
        total = d1 + d2
        state['player_dice1'], state['player_dice2'] = d1, d2
        if total == 2:
            state['round_points'] = 0
            state['turn'] = 'ghost'
            state['message'] = 'Snake eyes! No points. Ghost\'s turn.'
        else:
            state['round_points'] += total
            state['message'] = f'You rolled {d1}+{d2}={total}. Turn: {state["round_points"]} points.'

    elif mode == 'craps':
        d1, d2 = roll_dice(), roll_dice()
        total = d1 + d2
        state['player_dice1'], state['player_dice2'] = d1, d2
        if state['come_out']:
            if total in (7, 11):
                state['game_over'], state['winner'] = True, 'player'
                state['message'] = f'Come-out {total}! You win!'
            elif total in (2, 3, 12):
                state['game_over'], state['winner'] = True, 'ghost'
                state['message'] = f'Come-out {total}! You lose.'
            else:
                state['come_out'] = False
                state['point'] = total
                state['message'] = f'Point set to {total}. Roll again.'
        else:
            if total == state['point']:
                state['game_over'], state['winner'] = True, 'player'
                state['message'] = f'You hit the point {total}! You win!'
            elif total == 7:
                state['game_over'], state['winner'] = True, 'ghost'
                state['message'] = f'You rolled a 7! You lose.'
            else:
                state['message'] = f'You rolled {total}. Need {state["point"]} or 7.'
    return state

def player_hold(state):
    if state['game_over'] or state['turn'] != 'player':
        return state
    if state['mode'] in ('pig_single', 'pig_two'):
        state['player_score'] += state['round_points']
        state['round_points'] = 0
        state['turn'] = 'ghost'
        state['message'] = f'You hold with {state["player_score"]} points. Ghost\'s turn.'
    return state

def ghost_roll(state):
    """Perform a single ghost roll. Returns updated state."""
    if state['game_over'] or state['turn'] != 'ghost':
        return state

    mode = state['mode']
    if mode == 'pig_single':
        roll = roll_dice()
        state['ghost_dice1'] = roll
        if roll == 1:
            state['ghost_round_points'] = 0
            state['turn'] = 'player'
            state['message'] = 'Ghost rolled a 1! No points. Your turn.'
        else:
            state['ghost_round_points'] += roll
            if state['ghost_score'] + state['ghost_round_points'] >= 100:
                state['ghost_score'] += state['ghost_round_points']
                state['ghost_round_points'] = 0
                state['game_over'] = True
                state['winner'] = 'ghost'
                state['message'] = f'Ghost rolled {roll} and reached 100! Ghost wins!'
            elif state['ghost_round_points'] >= 20:
                state['ghost_score'] += state['ghost_round_points']
                state['ghost_round_points'] = 0
                state['turn'] = 'player'
                state['message'] = f'Ghost holds with {state["ghost_score"]} points. Your turn.'
            else:
                state['message'] = f'Ghost rolled {roll}. Ghost turn points: {state["ghost_round_points"]}.'

    elif mode == 'pig_two':
        d1, d2 = roll_dice(), roll_dice()
        total = d1 + d2
        state['ghost_dice1'], state['ghost_dice2'] = d1, d2
        if total == 2:
            state['ghost_round_points'] = 0
            state['turn'] = 'player'
            state['message'] = 'Ghost rolled snake eyes! No points. Your turn.'
        else:
            state['ghost_round_points'] += total
            if state['ghost_score'] + state['ghost_round_points'] >= 100:
                state['ghost_score'] += state['ghost_round_points']
                state['ghost_round_points'] = 0
                state['game_over'] = True
                state['winner'] = 'ghost'
                state['message'] = f'Ghost rolled {d1}+{d2}={total} and reached 100! Ghost wins!'
            elif state['ghost_round_points'] >= 20:
                state['ghost_score'] += state['ghost_round_points']
                state['ghost_round_points'] = 0
                state['turn'] = 'player'
                state['message'] = f'Ghost holds with {state["ghost_score"]} points. Your turn.'
            else:
                state['message'] = f'Ghost rolled {d1}+{d2}={total}. Ghost turn points: {state["ghost_round_points"]}.'

    elif mode == 'craps':
        # Ghost doesn't roll in craps
        state['turn'] = 'player'
    return state

def check_winner(state):
    if state['mode'] in ('pig_single', 'pig_two'):
        if state['player_score'] >= 100:
            state['game_over'], state['winner'] = True, 'player'
            state['message'] = 'You reached 100! You win!'
        elif state['ghost_score'] >= 100:
            state['game_over'], state['winner'] = True, 'ghost'
            state['message'] = 'Ghost reached 100! Ghost wins!'
    return state

# ----- Routes -----
@app.route('/')
def index():
    return render_template('game.html')

@app.route('/api/new', methods=['POST'])
def api_new():
    mode = request.get_json().get('mode', 'pig_single')
    session['game'] = new_game(mode)
    return jsonify(session['game'])

@app.route('/api/roll', methods=['POST'])
def api_roll():
    if 'game' not in session:
        session['game'] = new_game()
    state = session['game']
    state = player_roll(state)
    state = check_winner(state)
    session['game'] = state
    # If game not over and it's ghost's turn, we will not process the ghost's full turn here.
    # The client will call /api/ghost_roll repeatedly.
    return jsonify(state)

@app.route('/api/hold', methods=['POST'])
def api_hold():
    if 'game' not in session:
        session['game'] = new_game()
    state = session['game']
    state = player_hold(state)
    state = check_winner(state)
    session['game'] = state
    # Again, let the client handle ghost turns via repeated calls.
    return jsonify(state)

@app.route('/api/ghost_roll', methods=['POST'])
def api_ghost_roll():
    """Perform one ghost roll. Returns updated state."""
    if 'game' not in session:
        session['game'] = new_game()
    state = session['game']
    state = ghost_roll(state)
    state = check_winner(state)
    session['game'] = state
    return jsonify(state)

@app.route('/api/status', methods=['GET'])
def api_status():
    if 'game' not in session:
        session['game'] = new_game()
    return jsonify(session['game'])

if __name__ == '__main__':
    app.run(debug=True)