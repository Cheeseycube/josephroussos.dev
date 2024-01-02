import oracledb
import os
from dotenv import load_dotenv
import bcrypt
from dahuffman import HuffmanCodec
import sys

# If using oracle (locally hosted database): https://www.oracle.com/database/technologies/appdev/python/quickstartpythononprem.html

# If using oracle autonomous database: https://www.oracle.com/database/technologies/appdev/python/quickstartpython.html


''' Documentation:
        Games Table:
            userID int                                      # Foreign Key for USERS
            pgnID int                                       # Foreign Key for PGNS
            gameID NUMBER generated by default as identity  # Primary Key
            datePlayed date
            platform varchar(20)                            # chess.com, lichess, otb, etc...
            white varchar(50)
            black varchar(50)
            white_elo number(4)
            black_elo number(4)
            game_result varchar(5)
            termination varchar(70)
            time_control number(4)
            link varchar(60)
            
        Users Table:
            userID NUMBER generated by default as identity   # Primary Key
            userName varchar(50) UNIQUE                      # If a null value is provided, internal app logic should prevent insertion
            userPassword raw(70) UNIQUE                      # If a null value is provided, internal app logic should prevent insertion
            hashSalt raw(40)                                 # This will probably be unique and will never be null
            
        PGNS Table:
            pgnID NUMBER generated by default as identity    # Primary Key
            pgn raw(4000) UNIQUE                             # equivalent to varbinary(4000)
            '''

# connection pools will be stored in this global variable
pool = None

def addPGN(game, encoded_pgn):
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting addPGN operation")
        return {'id': -1, 'isDuplicate': False}
    connection = pool.acquire()
    cursor = connection.cursor()

    # try to add the pgn, if duplicate found return original
    pgn_id = cursor.var(int)
    sql_statement = "insert into PGNS(PGN) values(:pgn_bv) returning PGNID into :id_bv"
    try:
        cursor.execute(sql_statement, [encoded_pgn, pgn_id])
        connection.commit()
        # returning new pgn's id number
        return {'id': pgn_id.getvalue()[0], 'isDuplicate': False}
    except oracledb.DataError as e:
        error_obj, = e.args
        print("error adding pgn to database, see errors.txt")
        print(f"error message: {error_obj}")
        error_file = open(os.getenv('CHESS_ERRORS_PATH'), 'a')
        error_file.write(game.pgn + "\n")
        error_file.write(game.link + "\n\n")
        error_file.close()
        connection.commit()
        # returning -1 means the pgn was not added and there is no duplicate
        return {'id': -1, 'isDuplicate': False}
    except oracledb.IntegrityError as e:
        error_obj = e.args
        #print("Duplicate pgn was not added, returning original pgn's id number, see errors.txt for the affected pgn")
        print(f"error message: {error_obj}")
        error_file = open(os.getenv('CHESS_ERRORS_PATH'), 'a')
        error_file.write(game.pgn + "\n")
        error_file.write(game.link + "\n\n")
        error_file.close()
        connection.commit()
        # returning the original in the case of a duplicate
        sql_statement = "select PGNID from PGNS WHERE PGN = :encoded_pgn_bv"
        cursor.execute(sql_statement, [encoded_pgn])
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        data = cursor.fetchone()
        if data is None:
            print("unknown error on line 86 in ChessDatabase.py")
        else:
            return {'id': data["PGNID"], 'isDuplicate': True}

    return {'id': -1, 'isDuplicate': False}


# Returns a huffman-encoded pgn
def getPGN(idNum):
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting getPGN operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()

    sql_statement = "select PGN from PGNS where PGNID = :id_bv"
    cursor.execute(sql_statement, [idNum])
    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchone()
    if data is None:
        return -1
    return data['PGN']


def decodePGN(encoded_pgn):
    # training the huffman encoder
    training_file = open(os.getenv('TRAINING_DATA_DIR'), 'r')
    training_data = training_file.read()
    codec = HuffmanCodec.from_data(training_data)
    return codec.decode(encoded_pgn)


# This disallows duplicates for the same user
def add_multiple_Games(Games, userID, platform):
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting add_multiple_Games operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()

    # training the huffman encoder
    training_file = open(os.getenv('TRAINING_DATA_DIR'), 'r')
    training_data = training_file.read()
    codec = HuffmanCodec.from_data(training_data)

    for game in Games.games:

        # encode each game's pgn
        try:
            encoded_game = codec.encode(game.pgn)
        except:
            print("could not encode a game: see errors.txt for the affected pgn", file=sys.stderr)
            error_file = open(os.getenv('CHESS_ERRORS_PATH'), 'a')
            error_file.write(game.pgn + "\n")
            error_file.write(game.link + "\n\n")
            error_file.close()
            continue

        # add each game's pgn to the pgn table and get the corresponding id num
        # addPgn() will detect duplicates
        pgn_id = addPGN(game, encoded_game)

        if pgn_id['isDuplicate']:
            # check if the given user has this pgn already
            matches = cursor.execute("select 1 from GAMES where PGNID = :id_bv", id_bv=pgn_id['id'])
            for row in matches:
                if row[0] is not None:
                    print("The provided pgn has been uploaded already by the same user, cancelling add")
                    pgn_id['id'] = -1
                else:
                    break

        # if this is true then there is either a duplicate pgn or an error occurred when uploading the pgn
        if pgn_id['id'] == -1:
            # error message should have been generated already
            continue

        # add each game to the games table

        print(f"add multiple games: userId: {userID} pgnID: {pgn_id['id']}")
        print(f"{game.link}")
        date = game.date.replace(".", "-")
        print(date)
        #time control with increment is kinda broken
        sql_statement = ("insert into Games(USERID, PGNID, DATEPLAYED, PLATFORM, WHITE, BLACK, WHITE_ELO, BLACK_ELO, TIME_CONTROL)"
                         "values(:id_bv, :pgn_id_bv, TO_DATE(:date_bv, 'YYYY-MM-DD'), :platform_bv, :white_bv, :black_bv, :white_elo_bv, :black_elo_bv, :time_control_bv)")
        cursor.execute(sql_statement,
                       [userID, pgn_id['id'], date, platform, game.white, game.black, int(game.white_elo),
                        int(game.black_elo), game.time_control])

    connection.commit()


# I think this only returns one game
def get_games_by_date(userID, date):
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting add_multiple_Games operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()

    # get pgn id
    sql_statement = ("select PGNID from Games where DATEPLAYED = TO_DATE(:date_bv, 'YYYY-MM-DD') and USERID = :id_bv")
    cursor.execute(sql_statement, [date, userID])
    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchone()
    if data is None:
        return "no games found"

    # get the encoded pgn
    pgn = getPGN(data["PGN"])

    # training the huffman encoder
    training_file = open('training_data.txt', 'r')
    training_data = training_file.read()
    codec = HuffmanCodec.from_data(training_data)
    # returning decoded pgn
    return codec.decode(pgn)


def get_most_recent_game(userID):
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting get_most_recent_game operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()

    sql_statement = "select MAX(DATEPLAYED) from Games where USERID = :id_bv"
    cursor.execute(sql_statement, [userID])

    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    latest_date = cursor.fetchone()
    print(latest_date['MAX(DATEPLAYED)'])

    sql_statement = ("select PGNID from Games where DATEPLAYED = :latest_date_bv")
    cursor.execute(sql_statement, [latest_date['MAX(DATEPLAYED)']])

    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchone()
    if (data is None):
        return "no games found"
    pgn_id = data["PGNID"]

    pgn = getPGN(pgn_id)
    # training the huffman encoder
    training_file = open('training_data.txt', 'r')
    training_data = training_file.read()
    codec = HuffmanCodec.from_data(training_data)
    return codec.decode(pgn)


# returns a list of game dictionaries ordered by date
def get_all_games(userID):
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting get_most_recent_game operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()

    sql_statement = ("select * from Games where USERID = :id_bv order by DATEPLAYED DESC")
    cursor.execute(sql_statement, [userID])

    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchall()
    connection.commit()
    if data is None:
        return []
    return data


# Returns a single game based off a unique id number
def get_game_by_id(given_id):
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting add_multiple_Games operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()

    sql_statement = ("select * from Games where GAMEID = :id_bv")
    cursor.execute(sql_statement, [given_id])
    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchone()
    connection.commit()
    return data


# Uses the global field "pool" as defined by makeConnectionPool
def addUser(userName, password):
    # checking for valid inputs
    if userName is None:
        print("cannot insert null userName")
        return -1
    if password is None:
        print("cannot insert null password")
        return -1

    if (len(userName) < 1 or len(userName) > 45):
        return -1, "Username must be between 1 and 45 characters"
    if (len(password) < 7 or len(password) > 65):
        return -1, "Password must be between 7 and 65 characters"

    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting addUser operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()
    id_num = cursor.var(int)

    # hashing the password
    password = bytes(password, 'utf-8')
    salt = bcrypt.gensalt()
    password_hashed = bcrypt.hashpw(password, salt)

    # Is the userName available?
    matches = cursor.execute("select 1 from Users where userName = :userName_bv", userName_bv=userName)
    for row in matches:
        if row[0] is not None:
            print("The provided username has already been taken, please provide another one")
            connection.commit()
            return -1, "The provided username has already been taken, please provide another one"

    # Is the password (post-hashing) available?
    matches = cursor.execute("select 1 from Users where userPassword = :userPassword_bv",
                             userPassword_bv=password_hashed)
    for row in matches:
        if row[0] is not None:
            print("The provided password has already been taken, please provide another one")
            connection.commit()
            return -1, "The provided password has already been taken, please provide another one"

    # inserting into the database
    sql_statement = ("insert into Users (userName, userPassword, hashSalt)"
                     "values (:userName_bv, :userPassword_bv, :hashSalt_bv)"
                     "returning userID into :id_bv")
    try:
        cursor.execute(sql_statement, [userName, password_hashed, salt, id_num])
    except oracledb.IntegrityError:
        print("Your password or username is already in use, aborting add operation.")
        connection.commit()
        return -1, "Your password or username is already in use, aborting add operation."

    print(f"Successfully added {userName} to the database with an id of {id_num.getvalue()[0]}")
    connection.commit()
    # returning the new user's id number
    return id_num.getvalue()[0], f"Successfully added {userName} to the database with an id of {id_num.getvalue()[0]}"


def check_credentials(userName, password):
    global pool
    if pool is None:
        print("Connection pool was null, aborting verify password operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()

    cursor.execute("select * from Users where userName = :userName_bv", userName_bv=userName)
    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchone()
    if data is None:
        print("invalid username")
        connection.commit()
        return (False, 'invalid username')
    else:
        original_password_hashed = data['USERPASSWORD']
        given_password = bytes(password, 'utf-8')
        given_password_hashed = bcrypt.hashpw(given_password, data['HASHSALT'])
        if original_password_hashed == given_password_hashed:
            connection.commit()
            return (True, None)
        else:
            print("invalid password")
            connection.commit()
            return (False, 'invalid password')


# returns a single connection to the database: mainly used for testing
def makeConnection():
    connection = oracledb.connect(
        user=os.getenv("ORACLE_USERNAME"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_CONNECTION_STRING"),
        #config_dir="../Wallet_ChessDB",
        #wallet_location="Wallet_ChessDB",
        #wallet_password=os.getenv("ORACLE_WALLET_PASSWORD")
    )
    print("connection established")
    return connection


# sets the global "pool" variable for use by other functions
def makeConnectionPool(pool_size):
    pool_min = pool_size
    pool_max = pool_size
    pool_inc = 0
    pool_gmd = oracledb.SPOOL_ATTRVAL_WAIT
    _pool = oracledb.SessionPool(user=os.getenv("ORACLE_USERNAME"),
                                 password=os.getenv("ORACLE_PASSWORD"),
                                 dsn=os.getenv("ORACLE_CONNECTION_STRING"),
                                 #config_dir="../Oracle Wallet",
                                 #wallet_location="Oracle Wallet",
                                 #wallet_password=os.getenv("PASSWORD"),
                                 min=pool_min,
                                 max=pool_max,
                                 increment=pool_inc,
                                 threaded=True,
                                 getmode=pool_gmd)
    global pool
    pool = _pool
    print("connection pool established")


def clearDatabase():
    connection = makeConnection()
    cursor = connection.cursor()  # defining cursor for later use
    cursor.execute("drop table Games")
    cursor.execute("drop table Users")
    cursor.execute("drop table PGNS")
    connection.commit()
    print("database cleared")


def initializeDatabase():
    connection = makeConnection()
    cursor = connection.cursor()  # defining cursor for later use
    # create Users and Games tables
    cursor.execute("""
    create table Users(userID NUMBER generated by default as identity, 
    userName varchar(50) UNIQUE, 
    userPassword raw(70) UNIQUE, 
    hashSalt raw(40), 
    PRIMARY KEY (userID))""")

    cursor.execute("""
    create table PGNS(pgnID NUMBER generated by default as identity, 
    PRIMARY KEY (pgnID), 
    pgn raw(4000) UNIQUE )""")

    cursor.execute("""
    create table Games(userID int, FOREIGN KEY (userID) REFERENCES USERS(userID) ON DELETE CASCADE, 
    pgnID int, FOREIGN KEY (pgnID) REFERENCES PGNS(pgnID) ON DELETE CASCADE, 
    gameID NUMBER generated by default as identity,
    PRIMARY KEY (gameID), 
    datePlayed date, 
    platform varchar(20), 
    white varchar(50), 
    black varchar(50),
    white_elo number(4), 
    black_elo number(4), 
    game_result varchar(5), 
    termination varchar(70),
    time_control number(4), 
    link varchar(60))""")

    connection.commit()
    print("database initialized")


# returns some kind of list of all users
def get_allUsers():
    connection = makeConnection()
    cursor = connection.cursor()
    res = []
    for row in cursor.execute("select userName from Users"):
        res.append(row[0])
    return res


# returns a user dict or None if the user is not found
def getUser(user_name):
    load_dotenv()
    load_dotenv('/var/www/josephroussos.dev/.env')
    makeConnectionPool(4)
    # setting up the connection
    global pool
    if pool is None:
        print("Connection pool was null, aborting getUser operation")
        return -1
    connection = pool.acquire()
    cursor = connection.cursor()
    cursor.execute("select * from Users where USERNAME = :name_bv", [user_name])
    columns = [col[0] for col in cursor.description]
    cursor.rowfactory = lambda *args: dict(zip(columns, args))
    data = cursor.fetchone()
    connection.commit()
    return data


if __name__ == '__main__':
    load_dotenv()
    print("welcome")
    #clearDatabase()
    initializeDatabase()

    # print(get_allUsers())
    # makeConnection()
    # makeConnectionPool(4)
    # print(get_all_games(1))
