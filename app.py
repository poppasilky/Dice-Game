from flask import Flask, render_template, request, redirect, url_for, session
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