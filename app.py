import json
from flask import Flask, render_template, request, flash, jsonify
import flask
import ChessApp.ChessDatabase as ChessDB
import ChessApp.ChessCom as ChessCom
import secrets
from dotenv import load_dotenv
import chess.pgn as chess_pgn
import io
from datetime import timedelta
from WordleApp.Wordle import *

# intitializing the app
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
#app.secret_key = 'secret-key'

# custom login--not flask login
class User:
    def __init__(self, name, id):
        self.name = name
        self.id = id


def convert_seconds(seconds):
    if seconds < 60:
        if seconds < 10:
            return f"0:0{seconds:.1f}"
        else:
            return f"0:{seconds:.1f}"
    if seconds < 3600:  # Less than an hour
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    else:  # An hour or more
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 3600) % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@app.route('/')
def index():
    return render_template('index.html')

####################### Chess #######################
user = User(None, None)
@app.route('/chess')
@app.route('/chess/<pageName>', methods=["GET", "POST"])
@app.route('/chess/analyze_game/<gameID>')
def chess(pageName=None, gameID=None):
    if gameID is not None:
        pageName = 'analyze_game'
    global user
    match pageName:
        case 'home':
            user.name = 'guest'
            user.id = ChessDB.getUser('guest')['USERID']
            return render_template('chess_home.html')
        case 'create_account':
            if request.method == "POST":
                user_name = request.form.get("userName")
                password = request.form.get("password")
                res = ChessDB.addUser(user_name, password)
                if res[0] == -1:
                    flash(res[1], 'error')
                    return render_template('chess_create_account.html')
                else:
                    flash(res[1])
                    return flask.redirect(flask.url_for('chess', pageName='login'))
            return render_template('chess_create_account.html')
        case 'login':
            if request.method == "POST":
                userName = request.form.get("userName")
                password = request.form.get("password")

                # checking credentials
                check_results = ChessDB.check_credentials(userName, password)

                # logging in
                if check_results[0]:
                    userData = ChessDB.getUser(userName)
                    if userData is None:
                        flash(f'error logging in as {userName}', 'error')
                        return render_template('chess_login_view.html')
                    user.name = userData['USERNAME']
                    user.id = userData['USERID']
                    return flask.redirect(flask.url_for('chess', pageName='profile'))
                else:
                    flash(check_results[1], 'error')
                    return render_template('chess_login_view.html')
            return render_template('chess_login_view.html')
        case 'profile':
            if user.name is None:
                return 'You must log in before accessing this page'
            if user.name == 'guest':
                flash('Logged in as guest')
            return render_template('chess_profile_view.html', name=user.name)
        case 'add_games':
            if user.name is None:
                return 'You must log in before accessing this page'
            if request.method == "POST":
                # add games
                print("add games tasks are executing")
                gameCol = ChessCom.GameCollection()
                gameCol.get_month_games(request.form.get("userName"), request.form.get("year"),
                                        request.form.get("month"))
                ChessDB.add_multiple_Games(gameCol, user.id, 'Chess.com')
                return flask.redirect(flask.url_for('chess', pageName='view_games'))
            return render_template('chess_add_games.html')
        case 'view_games':
            if user.id is None:
                return 'You must log in before accessing this page'
            games = ChessDB.get_all_games(user.id)
            return render_template('chess_view_games.html', name=user.name, games=games)
        case 'analyze_game':
            game = ChessDB.get_game_by_id(gameID)
            if game is None:
                return "No game found"
            encoded_pgn = ChessDB.getPGN(game['PGNID'])
            pgn = ChessDB.decodePGN(encoded_pgn)

            # Parse the PGN using python-chess library
            parsed_game = chess_pgn.read_game(io.StringIO(pgn))
            board = parsed_game.board()
            fen_positions = []

            # Iterate through the moves and collect FEN positions
            for move in parsed_game.mainline_moves():
                board.push(move)
                fen_positions.append(board.fen())

            # timestamp stuff
            timestamps = []
            timestamps_string = []

            # gives us a string in hh mm ss format
            for node in parsed_game.mainline():
                time_elapsed = node.clock()
                if time_elapsed is not None:
                    if (time_elapsed < 60):
                        time_elapsed = round(time_elapsed, 2)
                    else:
                        time_elapsed = int(time_elapsed)
                    # time_str = str(timedelta(seconds=time_elapsed))
                    time_str = convert_seconds(time_elapsed)
                    print(f"{node.move}: {time_elapsed}")
                    print(f"{node.move}: {time_str}")
                    timestamps.append(time_elapsed)
                    timestamps_string.append(time_str)

            # time control
            time_control = int(game['TIME_CONTROL'])
            time_control_string = str(timedelta(seconds=time_control))
            return render_template('chess_analyze_game.html', given_game=game, given_pgn=pgn, fen_positions=fen_positions,
                                   timestamps=timestamps, timestamps_string=timestamps_string, time_control=time_control,
                                   time_control_string=time_control_string)
        case _:
            return f'No route found: josephroussos.dev/chess/{pageName}'






####################### Wordle #######################
@app.route('/wordle', methods=["GET", "POST"])
def wordle():
    # maybe do something
    return render_template('wordle_home.html')

@app.route('/wordle_update', methods=['GET', 'POST'])
def wordle_update():
    enteredWord = request.args['enteredWord']
    colors = request.args.getlist('colors[]')
    remaining_words = request.args.getlist('remaining_words[]')

    wordleHelper = wordle_helper()
    feedback = []
    for color in colors:
        match color:
            case 'green':
                feedback.append(WordleCategory.HERE)
            case 'gray':
                feedback.append(WordleCategory.NOT_ANYWHERE)
            case _:
                feedback.append(WordleCategory.NOT_HERE)
    enteredWord = enteredWord.upper()


    matches = wordleHelper.find_feedback_matches(enteredWord, feedback, remaining_words)
    print(feedback)
    #print(colors)
    return matches
    #return jsonify({enteredWord: "from python!"})

if __name__ == '__main__':
    load_dotenv()
    load_dotenv('/var/www/josephroussos.dev/.env')
    ChessDB.makeConnectionPool(4)
    app.run(port=8080, debug=False)