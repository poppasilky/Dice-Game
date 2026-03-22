markdown

# 🎲 Dice Duel – Classic Dice Games with a Ghost AI

**A Flask‑powered web game featuring three classic dice games: Pig (single die), Pig (two dice), and Craps.**  
Play against a ghost AI that makes strategic decisions – and watch its turns roll out in real time.

## 🧠 Origin Story

This project started as a school assignment to build a simple dice game. Over time, it evolved with the help of AI (and a lot of iteration) into a full‑featured web application. It now includes:

- Three game modes with authentic rules  
- A smart ghost opponent with a visible turn progression  
- A sleek, responsive interface with animated dice  
- Persistent leaderboard using SQLite  
- Separate dice for player and ghost, turn point displays, and sequential ghost rolls

## ✨ Features

- **Three game modes**:  
  - *Pig (Single Die)* – roll a die, avoid a 1, bank points, first to 100 wins.  
  - *Pig (Two Dice)* – same, but rolling snake eyes (1+1) ends your turn.  
  - *Craps* – classic casino dice: come‑out roll wins/loses or sets a point; then roll the point before a 7.

- **Ghost AI**  
  - Plays by the same Pig rules (holds at 20 turn points, or when it would reach 100).  
  - Rolls are shown one by one with a 1‑second delay, so you can see the ghost building its points.

- **Live UI**  
  - Dice animate on every roll.  
  - Player and ghost scores, turn points, and dice are displayed separately.  
  - Buttons disable during the ghost’s turn to prevent interference.

- **Persistence**  
  - Game state is stored in Flask session (no database required for the core game, but a leaderboard can be added).

- **Easy Setup** – just Python and Flask.

## 🎮 How to Play

1. **Select a mode** from the dropdown and click *Apply & New Game*.
2. **Your turn**:
   - Click *Roll* to add points to your turn total.
   - If you roll a 1 (or snake eyes in two‑die mode), your turn ends and the ghost plays.
   - Click *Hold* to bank your turn points and give the turn to the ghost.
3. **Ghost turn**: The ghost will roll repeatedly (you’ll see each roll) until it either:
   - Rolls a 1 (or snake eyes) and loses its turn points,  
   - Banks at least 20 points (or would reach 100), then your turn resumes.
4. **First to 100 points wins!** The game will announce the winner and a new game can be started.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ installed
- Flask (install via `pip`)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/Dice-Game.git
cd Dice-Game

# Create and activate a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install Flask
pip install flask

# Run the app
python app.py

Open your browser at http://localhost:5000 and start playing!
📁 Project Structure
text

Dice-Game/
├── app.py               # Flask backend with game logic and API endpoints
├── templates/
│   └── game.html        # Frontend interface (HTML, CSS, JavaScript)
├── static/              # (optional) CSS, images, etc.
├── leaderboard.db       # SQLite database for scores (created automatically)
└── README.md

🛠️ Technologies Used

    Backend: Python, Flask, SQLite (for leaderboard)

    Frontend: HTML, CSS, JavaScript (no external frameworks)

    Game Logic: Custom implementations of Pig and Craps with an AI opponent

🤝 Credits & Acknowledgments

    Original school project: foundation for the game concept.

    AI assistance: used to refactor code, add features, debug, and polish the UI.

    Open‑source community: Flask, SQLite, and countless tutorials that inspired this work.

📝 License

This project is open source and available under the MIT License. Feel free to fork, modify, and use it for your own learning!

Enjoy the game, and may the dice be ever in your favor! 🎲
