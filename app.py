from flask import Flask, render_template, request, redirect, url_for, session
from random import randint
import json
import os

app = Flask(__name__)
rooms = {}
app.secret_key = "guess_game_secret"

# -------------------------
# Save files
# -------------------------

BEST_SCORE_FILE = "best_score.json"
HALL_OF_FAME_FILE = "hall_of_fame.json"

# -------------------------
# Create files if not exist
# -------------------------

if not os.path.exists(BEST_SCORE_FILE):
    with open(BEST_SCORE_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(HALL_OF_FAME_FILE):
    with open(HALL_OF_FAME_FILE, "w") as f:
        json.dump([], f)

# -------------------------
# Home
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")

# -------------------------
# Single Player
# -------------------------

@app.route("/single", methods=["GET", "POST"])
def single():

    if "number" not in session:
        session["number"] = randint(1, 100)
        session["attempts"] = 0

    message = ""

    if request.method == "POST":

        # প্রথমবার নাম save করবে
        if "player_name" not in session:
            session["player_name"] = request.form["name"]

        name = session["player_name"]

        guess = int(request.form["guess"])

        session["attempts"] += 1

        number = session["number"]

        if guess < number:

            message = "⬆ Guess Higher"

        elif guess > number:

            message = "⬇ Guess Lower"

        else:

            attempts = session["attempts"]

            with open(BEST_SCORE_FILE, "r") as f:
                scores = json.load(f)

            if attempts <= 2:

                update_hall_of_fame(
                    name,
                    attempts,
                    "singleplayer"
                )

            else:

                scores.append({
                    "name": name,
                    "score": attempts
                })

                scores = sorted(
                    scores,
                    key=lambda x: x["score"]
                )

            scores = scores[:5]

            with open(BEST_SCORE_FILE, "w") as f:
                json.dump(scores, f)

            session.pop("number", None)
            session.pop("attempts", None)

            message = f"🏆 Correct! You won in {attempts} attempts"

    with open(BEST_SCORE_FILE, "r") as f:
        scores = json.load(f)

    return render_template(
        "singleplayer.html",
        message=message,
        scores=scores
    )

@app.route("/reset-player", methods=["POST"])
def reset_player():

    session.pop("player_name", None)
    session.pop("number", None)
    session.pop("attempts", None)

    return redirect("/single")

@app.route("/create-room")
def create_room():
    return render_template("create_room.html")


@app.route("/join-room")
def join_room():
    return render_template("join_room.html")

@app.route("/create-room-submit", methods=["POST"])
def create_room_submit():

    name = request.form["name"]

    room_code = str(randint(1000, 9999))

    rooms[room_code] = {
        "host": name,

        "players": {
            name: {
                "secret": None,
                "attempts": 0,
                "finished": False,
                "guessed": [],
                "guess_attempts": {}
            }
        },

        "game_started": False
    }

    return redirect(
        f"/multiplayer/{room_code}/{name}"
    )

@app.route("/join-room-submit", methods=["POST"])
def join_room_submit():

    name = request.form["name"]
    room_code = request.form["room_code"]

    if room_code not in rooms:

        return """
        <h1>❌ Room Not Found</h1>
        <a href='/join-room'>Back</a>
        """

    rooms[room_code]["players"][name] = {
        "secret": None,
        "attempts": 0,
        "finished": False,
        "guessed": [],
        "guess_attempts": {}
    }

    return redirect(
        f"/multiplayer/{room_code}/{name}"
    )

@app.route(
    "/set-secret/<room_code>/<player_name>",
    methods=["GET", "POST"]
)
def set_secret(room_code, player_name):

    if room_code not in rooms:
        return "Room Not Found"

    if request.method == "POST":

        secret = int(
            request.form["secret"]
        )

        rooms[room_code]["players"][player_name]["secret"] = secret

        return redirect(
            f"/multiplayer/{room_code}/{player_name}"
        )

    return render_template(
        "set_secret.html",
        room_code=room_code,
        player_name=player_name
    )


@app.route(
    "/start-game/<room_code>/<player_name>"
)
def start_game(room_code, player_name):

    if room_code not in rooms:
        return "Room Not Found"

    room = rooms[room_code]

    for player in room["players"]:

        if room["players"][player]["secret"] is None:

            return f"""
            <h1>⚠ All players must set a secret number first.</h1>

            <a href='/multiplayer/{room_code}/{player_name}'>
                Back
            </a>
            """

    room["game_started"] = True

    return redirect(
        f"/guess-room/{room_code}/{player_name}"
    )

@app.route(
    "/guess-room/<room_code>/<player_name>"
)
def guess_room(room_code, player_name):

    room = rooms[room_code]

    guessed = room["players"][player_name]["guessed"]

    targets = []

    for player in room["players"]:

        if player != player_name and player not in guessed:

            targets.append(player)

    return render_template(
        "guess_room.html",
        room_code=room_code,
        player_name=player_name,
        targets=targets,
        attempts=room["players"][player_name]["attempts"]
    )

@app.route(
    "/guess/<room_code>/<player_name>/<target>",
    methods=["GET", "POST"]
)
def guess(room_code, player_name, target):

    room = rooms[room_code]

    secret = room["players"][target]["secret"]

    message = ""

    if request.method == "POST":

        user_guess = int(
            request.form["guess"]
        )

        room["players"][player_name]["attempts"] += 1

        if target not in room["players"][player_name]["guess_attempts"]:

            room["players"][player_name]["guess_attempts"][target] = 0

        room["players"][player_name]["guess_attempts"][target] += 1

        if user_guess < secret:

            message = "⬆ Guess Higher"

        elif user_guess > secret:

            message = "⬇ Guess Lower"

        else:

            room["players"][player_name]["guessed"].append(
                target
            )

            total_players = len(room["players"])

            guessed_count = len(
                room["players"][player_name]["guessed"]
            )

            if guessed_count == total_players - 1:

                room["players"][player_name]["finished"] = True

                return redirect(
                    f"/waiting/{room_code}/{player_name}"
                )

            return redirect(
                f"/guess-room/{room_code}/{player_name}"
            )

    return render_template(
        "guess.html",
        room_code=room_code,
        player_name=player_name,
        target=target,
        message=message,
        attempts=room["players"][player_name]["attempts"]
    )

@app.route(
    "/waiting/<room_code>/<player_name>"
)
def waiting(room_code, player_name):

    room = rooms[room_code]

    if all_finished(room):

        return redirect(
            f"/results/{room_code}"
        )

    return render_template(
        "waiting.html"
    )

@app.route(
    "/results/<room_code>"
)
def results(room_code):

    room = rooms[room_code]

    leaderboard = sorted(
        room["players"].items(),
        key=lambda x: x[1]["attempts"]
    )

    winner = leaderboard[0][0]

    top_3 = leaderboard[:3]

    for player_data in top_3:

        update_hall_of_fame(
            player_data[0],
            player_data[1]["attempts"],
            "multiplayer"
        )

    return render_template(
        "results.html",
        winner=winner,
        leaderboard=leaderboard
    )


@app.route(
    "/multiplayer/<room_code>/<player_name>"
)
def multiplayer(room_code, player_name):

    if room_code not in rooms:
        return "Room Not Found"

    room = rooms[room_code]

    return render_template(
        "multiplayer.html",
        room_code=room_code,
        player_name=player_name,
        players=room["players"]
    )

def all_finished(room):

    for player in room["players"]:

        if room["players"][player]["finished"] == False:

            return False

    return True

def update_hall_of_fame(name, attempt, mode):

    with open(HALL_OF_FAME_FILE, "r") as f:
        fame = json.load(f)

    found = False

    for player in fame:

        if (
            player["name"] == name
            and
            player["mode"] == mode
        ):

            player["records"] += 1

            if attempt < player["best_attempt"]:
                player["best_attempt"] = attempt

            found = True
            break

    if not found:

        fame.append({
            "name": name,
            "mode": mode,
            "best_attempt": attempt,
            "records": 1
        })

    with open(HALL_OF_FAME_FILE, "w") as f:
        json.dump(fame, f, indent=4)

# -------------------------
# Hall Of Fame
# -------------------------

@app.route("/hall")
def hall():

    with open(HALL_OF_FAME_FILE, "r") as f:
        hall = json.load(f)

    single_players = []
    multiplayer_players = []

    for player in hall:

        if player["mode"] == "singleplayer":
            single_players.append(player)

        elif player["mode"] == "multiplayer":
            multiplayer_players.append(player)

    return render_template(
        "hall.html",
        single_players=single_players,
        multiplayer_players=multiplayer_players
    )

if __name__ == "__main__":
    app.run(debug=True)