from flask import Flask, jsonify, render_template, url_for, redirect
import random
import string
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime
import logging

# --- Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Replace 'path/to/your/serviceAccountKey.json' with the actual path to your downloaded JSON file.
SERVICE_ACCOUNT_KEY_PATH = 'serviceAccountKey.json'

# Your Realtime Database URL (from your project details)
DATABASE_URL = 'https://bingo-17102-default-rtdb.firebaseio.com'

# --- Initialize Firebase Admin SDK ---
try:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })
    logger.info("Firebase Admin SDK initialized successfully.")
except Exception as e:
    logger.exception("Error initializing Firebase Admin SDK: %s", e)
    logger.error("Please ensure 'serviceAccountKey.json' is correctly placed and valid.")
    exit()
    
# --- Get a database reference ---
ref = db.reference('/') # Reference to the root of your database

app = Flask(__name__)


BINGO_NUMBERS = [n for n in range(1, 76)]
CALLED_NUMBERS = []


def get_bingo_board():
    board = [["B", "I", "N", "G", "O"]]
    chosen = []
    for i in range(5):
        row = []
        inc = 0
        for j in range(5):
            while True:
                num = random.randint(1, 15) + inc
                if num not in chosen:
                    break
            row.append(f"{num}")
            chosen.append(num)
            inc += 15
        board.append(row)
    board[3][2] = 'FREE'
    return board


def generate_game_id():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))


def generate_board_id(game_id):
    num_players = int(ref.child('game_ids').child(game_id).child('num_players').get())
    board_id = num_players + 1
    return board_id


def initialize_game():
    game_id = generate_game_id()

    new_game_data = {
        game_id: {
            "board_ids": {},
            "numbers": [],
            "num_players": 0,
            "expiration": datetime.datetime.now().timestamp() + 60 * 60 * 24, # Expire after 24 hours
        }
    }

    try:
        ref.child('game_ids').child(game_id).set(new_game_data)
        logger.info("Successfully initialized game '%s'.", game_id)
    except Exception as e:
        logger.exception("Error initializing game '%s': %s", game_id, e)
        
    return game_id


def initialize_board(game_id):
    board_id = generate_board_id(game_id)
    board = get_bingo_board()
    
    # Update num players and board
    try:
        ref.child('game_ids').child(game_id).child('num_players').set(board_id)
        ref.child('game_ids').child(game_id).child('board_ids').child(board_id).set(board)
        logger.info("Successfully initialized board '%s'.", board_id)
    except Exception as e:
        logger.exception("Error initializing board '%s': %s", board_id, e)
        
    return board_id
    

@app.route("/", methods=["GET"])
def index():
    board = get_bingo_board()
    return render_template("index.html", board=board)


@app.route("/get_next_number", methods=["GET"])
def get_next_number():
    global BINGO_NUMBERS, CALLED_NUMBERS

    num = BINGO_NUMBERS.pop(random.randint(0, len(BINGO_NUMBERS) - 1))

    brackets = {0: "B", 1: "I", 2: "N", 3: "G", 4: "O"}

    letter = brackets[num // 15]

    CALLED_NUMBERS.append(letter + str(num))
    return jsonify(
        {"letter": letter, "number": num, "previously_called": CALLED_NUMBERS}
    )


@app.route("/reset", methods=["GET"])
def reset():
    global BINGO_NUMBERS, CALLED_NUMBERS
    BINGO_NUMBERS = [n for n in range(1, 76)]
    CALLED_NUMBERS = []

    return jsonify({"success": True})


@app.route("/host", methods=["GET"])
def init_host():
    game_id = initialize_game()
    return redirect(url_for("host", game_id=game_id))


@app.route("/host/<game_id>", methods=["GET"])
def host(game_id):
    game_url = url_for("join", game_id=game_id)
    return render_template("host.html", game_id=game_id)

@app.route("/<game_id>", methods=["GET"])
def join(game_id):
    board_id = initialize_board(game_id)
    return render_template("join.html", game_id=game_id)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate, public, max-age=0"
    )
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
