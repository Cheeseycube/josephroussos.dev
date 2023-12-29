from flask import Flask, render_template, request, flash
import flask
import ChessApp.ChessDatabase as ChessDB
import ChessApp.ChessCom as ChessCom
import secrets
from dotenv import load_dotenv



# intitializing the app
app = Flask(__name__)
#app.secret_key = secrets.token_urlsafe(16)
app.secret_key = 'secret-key'

# custom login--not flask login
class User:
    def __init__(self, name, id):
        self.name = name
        self.id = id

@app.route('/')
def index():
    return render_template('index.html')

####################### Chess #######################
user = User(None, None)
@app.route('/chess')
@app.route('/chess/<pageName>', methods=["GET", "POST"])
def chess(pageName):
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
        case _:
            return f'No route found: josephroussos.dev/chess/{pageName}'



####################### Wordle #######################
@app.route('/wordle/<pageName>', methods=["GET", "POST"])
def wordle_page(pageName):
    return 'Wordle is kinda fun'

if __name__ == '__main__':
    load_dotenv()
    load_dotenv('/var/www/josephroussos.dev/.env')
    ChessDB.makeConnectionPool(4)
    app.run(port=8080, debug=False)