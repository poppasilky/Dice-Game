from flask import Flask, render_template, request, jsonify, session, g
import random
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
DATABASE = 'leaderboard.db'

# ----- Database Setup -----
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                player_score INTEGER,
                ghost_score INTEGER,
                winner TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# ----- Game Logic (Pig Dice) -----
def new_game():
    return {
        'player_score': 0,
        'ghost_score': 0,
        'current_roll': 0,
        'turn': 'player',  # 'player' or 'ghost'
        'round_points': 0,
        'game_over': False,
        'message': 'Roll the dice to start!'
    }

def roll_dice():
    return random.randint(1, 6)

def player_roll(state):
    if state['game_over']:
        return state
    if state['turn'] != 'player':
        state['message'] = "It's the ghost's turn."
        return state

    roll = roll_dice()
    state['current_roll'] = roll

    if roll == 1:
        state['round_points'] = 0
        state['turn'] = 'ghost'
        state['message'] = f'You rolled a 1! No points added. Ghost\'s turn.'
    else:
        state['round_points'] += roll
        state['message'] = f'You rolled a {roll}. You have {state["round_points"]} points this turn.'

    return state

def player_hold(state):
    if state['game_over']:
        return state
    if state['turn'] != 'player':
        state['message'] = "It's the ghost's turn."
        return state

    state['player_score'] += state['round_points']
    state['round_points'] = 0
    state['turn'] = 'ghost'
    state['message'] = f'You hold with {state["player_score"]} points. Ghost\'s turn.'
    return state

def ghost_turn(state):
    if state['game_over']:
        return state
    if state['turn'] != 'ghost':
        return state

    # Simple AI: roll until at least 20 points or risk a 1
    while state['turn'] == 'ghost' and not state['game_over']:
        roll = roll_dice()
        if roll == 1:
            state['round_points'] = 0
            state['turn'] = 'player'
            state['message'] = 'Ghost rolled a 1! No points added. Your turn.'
            break
        else:
            state['round_points'] += roll
            # If ghost reaches 20 or more this turn, hold
            if state['ghost_score'] + state['round_points'] >= 100:
                state['ghost_score'] += state['round_points']
                state['round_points'] = 0
                state['game_over'] = True
                state['winner'] = 'ghost'
                state['message'] = f'Ghost rolled and reached 100 points! Ghost wins!'
                break
            elif state['round_points'] >= 20:
                state['ghost_score'] += state['round_points']
                state['round_points'] = 0
                state['turn'] = 'player'
                state['message'] = f'Ghost holds with {state["ghost_score"]} points. Your turn.'
                break
    return state

def check_winner(state):
    if state['player_score'] >= 100:
        state['game_over'] = True
        state['winner'] = 'player'
        state['message'] = 'You reached 100 points! You win!'
        # Save to database
        save_game_result('Player', state['player_score'], state['ghost_score'], 'player')
    elif state['ghost_score'] >= 100:
        state['game_over'] = True
        state['winner'] = 'ghost'
        state['message'] = 'Ghost reached 100 points! Ghost wins!'
        save_game_result('Player', state['player_score'], state['ghost_score'], 'ghost')
    return state

def save_game_result(player_name, player_score, ghost_score, winner):
    db = get_db()
    db.execute('INSERT INTO games (player_name, player_score, ghost_score, winner) VALUES (?, ?, ?, ?)',
               (player_name, player_score, ghost_score, winner))
    db.commit()

def get_leaderboard():
    db = get_db()
    cur = db.execute('SELECT player_name, player_score, ghost_score, winner, timestamp FROM games ORDER BY timestamp DESC LIMIT 10')
    return cur.fetchall()

# ----- Flask Routes -----
@app.route('/')
def index():
    return render_template('game.html')

@app.route('/api/new', methods=['POST'])
def api_new():
    session['game'] = new_game()
    return jsonify(session['game'])

@app.route('/api/roll', methods=['POST'])
def api_roll():
    if 'game' not in session:
        session['game'] = new_game()
    state = session['game']
    if state['turn'] == 'player':
        state = player_roll(state)
        state = check_winner(state)
        session['game'] = state
        if not state['game_over'] and state['turn'] == 'ghost':
            state = ghost_turn(state)
            state = check_winner(state)
            session['game'] = state
        return jsonify(state)
    else:
        return jsonify({'error': 'Not your turn'}), 400

@app.route('/api/hold', methods=['POST'])
def api_hold():
    if 'game' not in session:
        session['game'] = new_game()
    state = session['game']
    if state['turn'] == 'player':
        state = player_hold(state)
        state = check_winner(state)
        session['game'] = state
        if not state['game_over'] and state['turn'] == 'ghost':
            state = ghost_turn(state)
            state = check_winner(state)
            session['game'] = state
        return jsonify(state)
    else:
        return jsonify({'error': 'Not your turn'}), 400

@app.route('/api/status', methods=['GET'])
def api_status():
    if 'game' not in session:
        session['game'] = new_game()
    return jsonify(session['game'])

@app.route('/api/leaderboard', methods=['GET'])
def api_leaderboard():
    leaderboard = get_leaderboard()
    return jsonify([dict(row) for row in leaderboard])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
