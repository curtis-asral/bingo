from flask import Flask, jsonify, render_template
import random

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
