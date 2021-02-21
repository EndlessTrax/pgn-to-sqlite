import re
import sqlite3


def convert_to_snake_case(value: str) -> str:
    """Convert any camal case attribute name to snake case"""
    return re.compile(r"(.)([A-Z][a-z]+)").sub(r"\1_\2", value).lower()


def create_db_connection(path: str):
    """"""
    db_connection = None
    try:
        db_connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

    return db_connection


def execute_query(db_connection, query: str):
    """"""
    cursor = db_connection.cursor()
    try:
        cursor.execute(query)
        db_connection.commit()
        print("Query executed successfully")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


def create_games_table(db_connection):
    """"""
    execute_query(
        db_connection,
        """CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            site TEXT,
            date TEXT,
            round TEXT,
            white TEXT,
            black TEXT,
            result TEXT,
            eco TEXT,
            utc_date TEXT,
            utc_time TEXT,
            white_elo TEXT,
            black_elo TEXT,
            variant TEXT,
            time_control TEXT,
            termination TEXT
            );
        """,
    )


def build_pgn_dict(pgn: str) -> dict:
    """"""
    game_dict = dict()
    pgn_lines = pgn.split("\n")

    for line in pgn_lines:
        if line.startswith("["):

            key_pattern = re.compile(r"([^\s]+)")
            value_pattern = re.compile(r"\"(.+?)\"")

            key = convert_to_snake_case(
                re.search(key_pattern, line).group().lstrip("[")
            )

            value = re.search(value_pattern, line)

            if value is not None:
                game_dict[key] = value.group().strip('"')
            else:
                game_dict[key] = ""

        elif line.startswith("1."):
            game_dict["moves"] = line

    return game_dict


def save_game_to_db(game: dict):
    """"""
    query = f"""INSERT INTO games (
        event,
        site,
        date,
        round,
        white,
        black,
        result,
        eco,
        utc_date,
        utc_time,
        white_elo,
        black_elo,
        variant,
        time_control,
        termination
    )
    VALUES (
        '{game['event']}',
        '{game['site']}',
        '{game['date']}',
        '{game['round'] if 'round' in game.values() else ''}',
        '{game['white']}',
        '{game['black']}',
        '{game['result']}',
        '{game['eco']}',
        '{game['utc_date']}',
        '{game['utc_time']}',
        '{game['white_elo']}',
        '{game['black_elo']}',
        '{game['variant'] if 'variant' in game.values() else ''}',
        '{game['time_control']}',
        '{game['termination']}'
    );
    """

    return query
