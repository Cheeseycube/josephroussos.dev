import json
import plotly.utils
from flask import Flask, render_template, request, flash, send_from_directory
import os
import flask
import ChessApp.ChessDatabase as ChessDB
import ChessApp.ChessCom as ChessCom
import secrets
from dotenv import load_dotenv
import chess.pgn as chess_pgn
import io
import plotly.io as pio
import plotly.graph_objects as go
from datetime import timedelta
from WordleApp.Wordle import *
from datetime import datetime
from CBA-Cycling.queryBuilder import queryBuilder
import traceback

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

####################### Chess ########################
user = User(None, None)
# TODO: Re-enable the Chess App once the database is refactored to Postgres
#@app.route('/chess')
#@app.route('/chess/<pageName>', methods=["GET", "POST"])
#@app.route('/chess/analyze_game/<gameID>')
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
####################### Chess ########################


####################### Wordle #######################
@app.route('/wordle', methods=["GET", "POST"])
def wordle():
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

    # this is a list of all possible words in alphabetical order
    matches = wordleHelper.find_feedback_matches(enteredWord, feedback, remaining_words)
    letter_plot = letter_distribution_plot(matches)

    payload = {
        'matches': matches,
        'letter_plot': letter_plot
    }
    return json.dumps(payload, cls=plotly.utils.PlotlyJSONEncoder)


def letter_distribution_plot(words):
    pio.templates.default = "plotly_dark"
    #letter_dict = {chr(i): [0] for i in range(ord('A'), ord('Z') + 1)}
    letter_dict = {
        'letter': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],
        'count': [0 for _ in range(26)]
    }
    for word in words:
        for letter in word:
            letter_dict['count'][ord(letter) - 65] += 1
            #print(f"{letter}: {ord(letter) - 65}")
    letter_df = pd.DataFrame.from_records(letter_dict)
    # only including non-zero values
    letter_df = letter_df.loc[letter_df['count'] > 0]
    #print(letter_df)
    fig = go.Figure(go.Bar(
        y=list(letter_df['letter']),
        x=list(letter_df['count']),
        text=[count for count in list(letter_df['count'])],
        textposition='auto',
        hovertemplate='%{text}',
        orientation='h'
    ))
    fig.update_layout(
        xaxis_title='Count',
        yaxis_title='Letters',
        title='Letter distribution',
    )

    return fig
####################### Wordle #######################


####################### Cycling #######################
@app.route('/cycling', methods=["GET", "POST"])
def cycling_home():
    """
    Page creation, modification, and controller method
    """
    current_year = datetime.today().year
    last_year = current_year - 1
    if request.method == 'POST':
        form_fields = ['startyear', 'endyear', 'placing', 'placing_filter', 'placing_end',
                       'age', 'age_filter', 'age_end', 'profile_score', 'profile_score_filter',
                       'profile_score_end', 'startlist_quality_score', 'startlist_quality_score_filter',
                       'startlist_quality_score_end', 'pcs_points', 'pcs_points_filter',
                       'pcs_points_end', 'uci_points', 'uci_points_filter', 'uci_points_end',
                       'pcs_points_trend', 'uci_points_trend', 'allow_other_teams',
                       'gc_filter', 'rank', 'rank_filter', 'rank_end', 'rank_year'
                       ]
        form_list_fields = ['race_classes', 'parcour_types', 'current_team_classes', 'past_teams_classes']
        all_fields = {}
        for field in form_fields:
            value = request.form.get(field)
            # print(f"{field}: {value}")
            if value is not None and value != '':
                all_fields[field] = value
        for field in form_list_fields:
            value = request.form.getlist(field)
            if len(value) > 0:
                all_fields[field] = value
        filters = create_filters(all_fields)
        query_builder = queryBuilder()
        try:
            returned_rider_info = query_builder.bigBuilder(filters, debug=True)
        except Exception:
            flash('Error applying the following filters:', 'error')
            for filterDict in filters:
                flash(str(filterDict), 'error')
            flash('Error Message:')
            flash(f'{traceback.format_exc()}', 'error')
            team_classes, race_classes, parcour_types = query_builder.query_template_arguments()
            return render_template('index.html',
                                   team_classes=team_classes,
                                   race_classes=race_classes,
                                   parcour_types=parcour_types,
                                   rider_info=[],
                                   current_year=current_year,
                                   last_year=last_year
                                   )

        rider_info_list = []
        for row in returned_rider_info:
            rider_info_list.append({'rider_url': row[0], 'name': row[1],
                                    'nationality': row[2], 'current_team': row[3],
                                    'birthdate': row[4], 'age': row[5]})
        team_classes, race_classes, parcour_types = query_builder.query_template_arguments()
        flash(f'Successfully applied the following filters:')
        for filterDict in filters:
            flash(str(filterDict))
        return render_template('index.html',
                               team_classes=team_classes,
                               race_classes=race_classes,
                               parcour_types=parcour_types,
                               rider_info=rider_info_list,
                               current_year=current_year,
                               last_year=last_year
                               )

    query_builder = queryBuilder()
    team_classes, race_classes, parcour_types = query_builder.query_template_arguments()
    return render_template("index.html",
                           team_classes=team_classes,
                           race_classes=race_classes,
                           parcour_types=parcour_types,
                           rider_info=[],
                           current_year=current_year,
                           last_year=last_year
                           )

def create_filters(field_dict: dict) -> list[dict]:
    """
    UI field to filter translator method to take the fields selected on the webpage and put the corresponding filter in a list[dict(str, str)] where the keys are the table, value, compare, and column to then give to the sqlBuilder

    Args:
        field_dict: contains fields selected by user on the webpage

    Returns:
        filters: contains translated filters to be used in sqlBuilder
    """
    filters = []
    # these are required fields in the form, so they should never be empty
    race_start_year_filter = {'table': 'race_info', 'column': 'year(date)', 'compare': '>=',
                              'value': field_dict['startyear']}
    race_end_year_filter = {'table': 'race_info', 'column': 'year(date)', 'compare': '<=',
                            'value': field_dict['endyear']}
    for key in field_dict.keys():
        match key:
            case 'gc_filter':
                match field_dict['gc_filter']:
                    case 'exclude':
                        if not has_filter_been_added(race_start_year_filter, filters):
                            filters.append(race_start_year_filter)
                        if not has_filter_been_added(race_end_year_filter, filters):
                            filters.append(race_end_year_filter)
                        filters.append(
                            {'table': 'race_info', 'column': 'is_total_results_page', 'compare': '=', 'value': '0'})
                    case 'include':
                        pass
                    case 'include-exclusive':
                        if not has_filter_been_added(race_start_year_filter, filters):
                            filters.append(race_start_year_filter)
                        if not has_filter_been_added(race_end_year_filter, filters):
                            filters.append(race_end_year_filter)
                        filters.append(
                            {'table': 'race_info', 'column': 'is_total_results_page', 'compare': '=', 'value': '1'})
            case 'placing':
                if not has_filter_been_added(race_start_year_filter, filters):
                    filters.append(race_start_year_filter)
                if not has_filter_been_added(race_end_year_filter, filters):
                    filters.append(race_end_year_filter)
                if (field_dict['placing_filter'] == 'between') and ('placing_end' in field_dict):
                    filters.append({'table': 'race_results', 'column': 'placement', 'compare': '>=',
                                    'value': field_dict['placing']})
                    filters.append({'table': 'race_results', 'column': 'placement', 'compare': '<=',
                                    'value': field_dict['placing_end']})
                else:
                    filters.append(
                        {'table': 'race_results', 'column': 'placement', 'compare': field_dict['placing_filter'],
                         'value': field_dict['placing']})
            case 'age':
                if (field_dict['age_filter'] == 'between') and ('age_end' in field_dict):
                    filters.append(
                        {'table': 'rider_info', 'column': 'age', 'compare': '>=', 'value': field_dict['age']})
                    filters.append(
                        {'table': 'rider_info', 'column': 'age', 'compare': '<=', 'value': field_dict['age_end']})
                else:
                    filters.append({'table': 'rider_info', 'column': 'age', 'compare': field_dict['age_filter'],
                                    'value': field_dict['age']})
            case 'profile_score':
                if not has_filter_been_added(race_start_year_filter, filters):
                    filters.append(race_start_year_filter)
                if not has_filter_been_added(race_end_year_filter, filters):
                    filters.append(race_end_year_filter)
                if (field_dict['profile_score_filter'] == 'between') and ('profile_score_end' in field_dict):
                    filters.append({'table': 'race_info', 'column': 'profile_score', 'compare': '>=',
                                    'value': field_dict['profile_score']})
                    filters.append({'table': 'race_info', 'column': 'profile_score', 'compare': '<=',
                                    'value': field_dict['profile_score_end']})
                else:
                    filters.append(
                        {'table': 'race_info', 'column': 'profile_score', 'compare': field_dict['profile_score_filter'],
                         'value': field_dict['profile_score']})
            case 'startlist_quality_score':
                if not has_filter_been_added(race_start_year_filter, filters):
                    filters.append(race_start_year_filter)
                if not has_filter_been_added(race_end_year_filter, filters):
                    filters.append(race_end_year_filter)
                if (field_dict['startlist_quality_score_filter'] == 'between') and (
                        'startlist_quality_score_end' in field_dict):
                    filters.append(
                        {'table': 'race_info', 'column': 'startlist_quality_score',
                         'compare': '>=',
                         'value': field_dict['startlist_quality_score']}
                    )
                    filters.append(
                        {'table': 'race_info', 'column': 'startlist_quality_score',
                         'compare': '<=',
                         'value': field_dict['startlist_quality_score_end']}
                    )
                else:
                    filters.append(
                        {'table': 'race_info', 'column': 'startlist_quality_score',
                         'compare': field_dict['startlist_quality_score_filter'],
                         'value': field_dict['startlist_quality_score']}
                    )
            case 'pcs_points':
                if not has_filter_been_added(race_start_year_filter, filters):
                    filters.append(race_start_year_filter)
                if not has_filter_been_added(race_end_year_filter, filters):
                    filters.append(race_end_year_filter)
                if (field_dict['pcs_points_filter'] == 'between') and ('pcs_points_end' in field_dict):
                    filters.append({'table': 'race_results', 'column': 'pcs_points', 'compare': '>=',
                                    'value': field_dict['pcs_points']})
                    filters.append({'table': 'race_results', 'column': 'pcs_points', 'compare': '<=',
                                    'value': field_dict['pcs_points_end']})
                else:
                    filters.append(
                        {'table': 'race_results', 'column': 'pcs_points', 'compare': field_dict['pcs_points_filter'],
                         'value': field_dict['pcs_points']})
            case 'uci_points':
                if not has_filter_been_added(race_start_year_filter, filters):
                    filters.append(race_start_year_filter)
                if not has_filter_been_added(race_end_year_filter, filters):
                    filters.append(race_end_year_filter)
                if (field_dict['uci_points_filter'] == 'between') and ('uci_points_end' in field_dict):
                    filters.append({'table': 'race_results', 'column': 'uci_points', 'compare': '>=',
                                    'value': field_dict['uci_points']})
                    filters.append({'table': 'race_results', 'column': 'uci_points', 'compare': '<=',
                                    'value': field_dict['uci_points_end']})
                else:
                    filters.append(
                        {'table': 'race_results', 'column': 'uci_points', 'compare': field_dict['uci_points_filter'],
                         'value': field_dict['uci_points']})
            case 'pcs_points_trend':
                if not has_filter_been_added(
                        {'table': 'trend', 'column': 'date', 'compare': '>=', 'value': field_dict['startyear']},
                        filters):
                    filters.append(
                        {'table': 'trend', 'column': 'date', 'compare': '>=', 'value': field_dict['startyear']})
                if not has_filter_been_added(
                        {'table': 'trend', 'column': 'date', 'compare': '<=', 'value': field_dict['endyear']}, filters):
                    filters.append(
                        {'table': 'trend', 'column': 'date', 'compare': '<=', 'value': field_dict['endyear']})
                filters.append({'table': 'trend', 'column': 'pcs_points', 'compare': field_dict['pcs_points_trend']})
            case 'uci_points_trend':
                if not has_filter_been_added(
                        {'table': 'trend', 'column': 'date', 'compare': '>=', 'value': field_dict['startyear']},
                        filters):
                    filters.append(
                        {'table': 'trend', 'column': 'date', 'compare': '>=', 'value': field_dict['startyear']})
                if not has_filter_been_added(
                        {'table': 'trend', 'column': 'date', 'compare': '<=', 'value': field_dict['endyear']},
                        filters):
                    filters.append(
                        {'table': 'trend', 'column': 'date', 'compare': '<=', 'value': field_dict['endyear']})
                filters.append({'table': 'trend', 'column': 'uci_points', 'compare': field_dict['uci_points_trend']})
            case 'rank':
                if 'rank_year' in field_dict:
                    filters.append({'table': 'rank', 'column': 'year', 'compare': '=',
                                    'value': field_dict['rank_year']})
                    if (field_dict['rank_filter'] == 'between') and ('rank_end' in field_dict):
                        filters.append(
                            {'table': 'rank', 'column': 'rank', 'compare': '>=', 'value': field_dict['rank']}
                        )
                        filters.append(
                            {'table': 'rank', 'column': 'rank', 'compare': '<=', 'value': field_dict['rank_end']}
                        )
                    else:
                        filters.append({'table': 'rank', 'column': 'rank', 'compare': field_dict['rank_filter'],
                                        'value': field_dict['rank']})
            case 'current_team_classes':
                for _class in field_dict['current_team_classes']:
                    filters.append(
                        {'table': 'team_info', 'column': 'class', 'compare': '=', 'value': _class}
                    )
            case 'race_classes':
                if not has_filter_been_added(race_start_year_filter, filters):
                    filters.append(race_start_year_filter)
                if not has_filter_been_added(race_end_year_filter, filters):
                    filters.append(race_end_year_filter)
                race_classes = field_dict['race_classes']
                if len(race_classes) > 1:
                    race_classes = tuple(race_classes)
                    filters.append(
                        {'table': 'race_info',
                         'column': 'class',
                         'compare': 'in',
                         'value': race_classes}
                    )
                else:
                    filters.append(
                        {'table': 'race_info', 'column': 'class', 'compare': '=', 'value': race_classes[0]}
                    )
            case 'past_teams_classes':
                filters.append({'table': 'team_history', 'column': 'season', 'compare': '>=',
                                'value': field_dict['startyear'], 'only_selected': False})
                filters.append({'table': 'team_history', 'column': 'season', 'compare': '<=',
                                'value': field_dict['endyear'], 'only_selected': False})
                for _class in field_dict['past_teams_classes']:
                    if ('allow_other_teams' not in field_dict):
                        filters.append(
                            {'table': 'team_history', 'column': 'class', 'compare': '=', 'value': _class,
                             'only_selected': True}
                        )
                    else:
                        filters.append(
                            {'table': 'team_history', 'column': 'class', 'compare': '=', 'value': _class,
                             'only_selected': False}
                        )
            case 'parcour_types':
                if not has_filter_been_added(race_start_year_filter, filters):
                    filters.append(race_start_year_filter)
                if not has_filter_been_added(race_end_year_filter, filters):
                    filters.append(race_end_year_filter)
                parcour_types = field_dict['parcour_types']
                if len(parcour_types) > 1:
                    parcour_types = tuple(parcour_types)
                    filters.append(
                        {'table': 'race_info',
                         'column': 'parcour_type',
                         'compare': 'in',
                         'value': parcour_types}
                    )
                else:
                    filters.append(
                        {'table': 'race_info', 'column': 'parcour_type', 'compare': '=', 'value': parcour_types[0]}
                    )

    return filters


def has_filter_been_added(given_filter: dict, filters: list[dict]) -> bool:
    """
    helper method for create_filters to check if a given filter has been created

    Args:
        given_filter: filter to check
        filters: list of filters already created
    Returns:
        True if filter has been added, False otherwise
    """
    for filterDict in filters:
        if (filterDict['table'] == given_filter['table'] and
                filterDict['column'] == given_filter['column'] and
                filterDict['compare'] == given_filter['compare']):
            return True
    return False


'''Documentation'''
@app.route('/docs')
def docs_home():
    return send_from_directory('site', 'overview/index.html')

@app.route('/app-reference/')
def app_docs():
    return send_from_directory('site', 'app-reference/index.html')

@app.route('/database-schema/')
def database_docs():
    return send_from_directory('site', 'database-schema/index.html')

@app.route('/dataCleaner-reference/')
def dataCleaner_docs():
    return send_from_directory('site', 'dataCleaner-reference/index.html')

@app.route('/dbBuilder-reference/')
def hubspot_docs():
    return send_from_directory('site', 'dbBuilder-reference/index.html')

@app.route('/dbUpdater-reference/')
def dbUpdater_docs():
    return send_from_directory('site', 'dbUpdater-reference/index.html')

@app.route('/documentation_maintenance/')
def documentation_maintenance_docs():
    return send_from_directory('site', 'documentation_maintenance/index.html')

@app.route('/error_handling/')
def error_handling_docs():
    return send_from_directory('site', 'error_handling/index.html')

@app.route('/overview/')
def overview_docs():
    return send_from_directory('site', 'overview/index.html')

@app.route('/queryBuilder-reference/')
def queryBuilder_docs():
    return send_from_directory('site', 'queryBuilder-reference/index.html')

@app.route('/Scraper-reference/')
def Scraper_docs():
    return send_from_directory('site', 'Scraper-reference/index.html')

@app.route('/db_tests-reference/')
def db_tests_docs():
    return send_from_directory('site', 'db_tests-reference/index.html')

@app.route('/queryBuilder_tests-reference/')
def queryBuilder_tests_docs():
    return send_from_directory('site', 'queryBuilder_tests-reference/index.html')

@app.route('/Scraper_tests-reference/')
def Scraper_tests_docs():
    return send_from_directory('site', 'Scraper_tests-reference/index.html')

@app.route('/user_guide/')
def user_guide_docs():
    return send_from_directory('site', 'user_guide/index.html')


site_dir = os.path.join(app.root_path, 'site')
@app.route('/<path:path>')
def serve_docs(path):
    return send_from_directory(site_dir, path)

####################### Cycling #######################



if __name__ == '__main__':
    load_dotenv()
    load_dotenv('/var/www/josephroussos.dev/.env')
    # TODO: re-enable the Chess App once the database is refactored to Postgres
    #ChessDB.makeConnectionPool(4)
    app.run(port=8080, debug=False)