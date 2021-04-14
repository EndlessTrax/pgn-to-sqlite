import re
import sqlite3

import berserk
import click
import requests


def convert_to_snake_case(value: str) -> str:
    """Convert any camel case attribute name to snake case"""
    return re.compile(r"(.)([A-Z][a-z]+)").sub(r"\1_\2", value).lower()


def build_pgn_dict(pgn: str) -> dict:
    """Takes any pgn text file and coverts to a dictionary object

    All pgn tags are converted to snake case. After converting, the dictionary
    is checked against a tuple of expected keys, and if missing, adds them with
    and empty string value. This ensures that each dictionary is uniform to
    match the database table.
    """
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

        # The move notation is a single line in the pgn.
        # The whole move notation is added to a single key:value
        elif line.startswith("1."):
            game_dict["moves"] = line

    expected_keys = (
        "event",
        "site",
        "date",
        "round",
        "white",
        "black",
        "result",
        "eco",
        "white_elo",
        "black_elo",
        "variant",
        "time_control",
        "termination",
        "moves",
    )

    # If an expected key isn't present in the dictionary representation of the 
    # pgn, then it is added with an empty string as its value.
    for key in expected_keys:
        if key not in game_dict:
            game_dict[key] = ""

    return game_dict


def save_game_to_db(conn, pgn: dict) -> None:
    """TODO:"""
    execute_db_query(
        conn,
        f"""INSERT INTO
        games (
            event,
            site,
            date,
            round,
            white,
            black,
            result,
            eco,
            white_elo,
            black_elo,
            variant,
            time_control,
            termination,
            moves)
        VALUES
        (
            '{pgn["event"]}',
            '{pgn["site"]}',
            '{pgn["date"]}',
            '{pgn["round"]}',
            '{pgn["white"]}',
            '{pgn["black"]}',
            '{pgn["result"]}',
            '{pgn["eco"]}',
            '{pgn["white_elo"]}',
            '{pgn["black_elo"]}',
            '{pgn["variant"]}',
            '{pgn["time_control"]}',
            '{pgn["termination"]}',
            '{pgn["moves"]}'
        );
        """,
    )


def fetch_chess_dotcom_games(user: str) -> list:
    """TODO:"""
    req = requests.get(f"https://api.chess.com/pub/player/{user}/games/archives")
    archive_urls = req.json()["archives"]
    games_list = []

    for url in archive_urls:
        archived_games = requests.get(url).json()["games"]

        for game in archived_games:
            games_list.append(game)

    print(f"INFO:    Total games imported from chess.com = {len(games_list)}")
    return games_list


def fetch_lichess_org_games(user: str) -> list:
    """TODO:"""
    client = berserk.Client()
    req = client.games.export_by_player(user, as_pgn=True)
    games_list = list(req)

    print(f"INFO:    Total games imported from lichess.org = {len(games_list)}")
    return games_list


def create_db_connection(path: str):
    """TODO:"""
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("INFO:    Connection to DB successful")
    except sqlite3.Error as e:
        print(f"Error:   The error '{e}' occurred")

    return connection


def execute_db_query(connection, query: str):
    """TODO:"""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


@click.command()
@click.argument("site")
@click.option(
    "-u",
    "--user",
    prompt="Enter your username for the site...",
    help="You username for the chess site",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
    prompt="Output path of the database...",
    help="Where you would like your database saved?",
)
def main(site, user, output):
    """
    Which SITE do you want to download your games from?
    You can download games from chess.com or lichess.org.\n
    ARGS:    chess    OR     lichess
    """

    db_conn = create_db_connection(output)
    execute_db_query(
        db_conn,
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
            white_elo INTEGER,
            black_elo INTEGER,
            variant TEXT,
            time_control TEXT,
            termination TEXT,
            moves TEXT
        );
        """,
    )
    print("INFO:    Created database and Games table")

    if site == "chess":
        print(f"INFO:    Fetching games for {user} from chess.com")

        games = fetch_chess_dotcom_games(user)
        for game in games:
            pgn_dict = build_pgn_dict(game["pgn"])
            save_game_to_db(db_conn, pgn_dict)

    elif site == "lichess":
        print(f"INFO:    Fetching games for {user} from lichess.org")

        games = fetch_lichess_org_games(user)
        for game in games:
            pgn_dict = build_pgn_dict(game)
            save_game_to_db(db_conn, pgn_dict)

    else:
        raise ValueError(
            f"'{site}' is not a valid site name. Check --help for valid inputs"
        )

    print(f"INFO:    Games saved to {output}")


if __name__ == "__main__":
    main()
