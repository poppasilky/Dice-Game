from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# ----- Game Logic (formerly in games/dice_game.py) -----

class DiceGame:
    @staticmethod
    def new_game():
        return {
            'turn': 'come_out',
            'point': None,
            'game_over': False,
            'message': 'New game! Roll the dice.',
            'rolls': [],
            'timestamp': datetime.now().isoformat()
        }

    @staticmethod
    def process_roll(state, roll):
        """Process a roll in a craps-like game."""
        if state['game_over']:
            state['message'] = 'Game is over. Start a new game.'
            return state

        # Store roll in history
        state['rolls'].append(roll)

        if state['turn'] == 'come_out':
            if roll in (7, 11):
                state['game_over'] = True
                state['message'] = f'You rolled {roll} – you win! 🎉'
                state['result'] = 'win'
            elif roll in (2, 3, 12):
                state['game_over'] = True
                state['message'] = f'You rolled {roll} – you lose! 💀'
                state['result'] = 'lose'
            else:
                state['turn'] = 'point'
                state['point'] = roll
                state['message'] = f'Point set to {roll}. Roll again to hit the point.'
        else:
            if roll == state['point']:
                state['game_over'] = True
                state['message'] = f'You rolled the point {roll}! You win! 🎉'
                state['result'] = 'win'
            elif roll == 7:
                state['game_over'] = True
                state['message'] = f'You rolled a 7 – you lose! 💀'
                state['result'] = 'lose'
            else:
                state['message'] = f'You rolled {roll}. Keep rolling to hit {state["point"]}.'
        return state

    @staticmethod
    def roll_dice():
        # Simulate two dice (2-12)
        return random.randint(1, 6) + random.randint(1, 6)

# ----- Helper Functions for Leaderboard -----

def get_leaderboard():
    """Retrieve leaderboard from session (or file/database)."""
    return session.get('leaderboard', [])

def update_leaderboard(result):
    """Add result to leaderboard (top 10)."""
    leaderboard = get_leaderboard()
    leaderboard.append({
        'result': result,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    # Keep only last 10 results
    session['leaderboard'] = leaderboard[-10:]

# ----- Routes -----

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'game' not in session:
        session['game'] = DiceGame.new_game()

    game = session['game']

    if request.method == 'POST':
        if 'new_game' in request.form:
            # Save result before resetting
            if game.get('result'):
                update_leaderboard(game['result'])
            session['game'] = DiceGame.new_game()
            return redirect(url_for('index'))

        if 'roll' in request.form:
            # Get roll value (could be from user input or random)
            roll = request.form.get('roll')
            if roll == 'random':
                roll = DiceGame.roll_dice()
            else:
                try:
                    roll = int(roll)
                except ValueError:
                    flash('Please enter a valid number (2-12).')
                    return redirect(url_for('index'))

            if 2 <= roll <= 12:
                game = DiceGame.process_roll(game, roll)
                session['game'] = game
            else:
                flash('Roll must be between 2 and 12.')

            # If game just ended, update leaderboard
            if game['game_over'] and 'result' in game:
                update_leaderboard(game['result'])

            return redirect(url_for('index'))

    # Render the HTML template
    return render_template('dice.html', game=game, leaderboard=get_leaderboard())

@app.route('/clear_leaderboard')
def clear_leaderboard():
    session.pop('leaderboard', None)
    flash('Leaderboard cleared.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)from flask import Flask, render_template, request, redirect, url_for, session
from games import dice_game

app = Flask(__name__)
app.secret_key = 'input-key'

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'game' not in session:
        session['game'] = dice_game.new_game()

    if request.method == 'POST':
        if 'new_game' in request.form:
            session['game'] = dice_game.new_game()
            return redirect(url_for('index'))

        if 'roll' in request.form:
            roll_str = request.form['roll']
            try:
                roll = int(roll_str)
                if roll < 2 or roll > 12:
                    session['game']['message'] = 'Error: Roll must be between 2 and 12.'
                else:
                    current = session['game']
                    session['game'] = dice_game.process_roll(current, roll)
            except ValueError:
                session['game']['message'] = 'Error: Please enter a whole number.'
            return redirect(url_for('index'))
        
        if 'random' in request.form:
            import random
            roll = random.randint(2, 12)
            current = session['game']
            session['game'] = dice_game.process_roll(current, roll)
            return redirect(url_for('index'))

    return render_template('dice.html', game=session['game'])

if __name__ == '__main__':
    app.run(debug=True)
