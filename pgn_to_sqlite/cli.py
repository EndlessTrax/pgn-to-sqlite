import re
import sqlite3
from pathlib import Path

import berserk
import click
import requests


def convert_to_snake_case(value: str) -> str:
    """Convert any camel case attribute name to snake case

    Args:
        value: The key to be converted to snake case

    Returns:
        The converted key
    """
    return re.compile(r"(.)([A-Z][a-z]+)").sub(r"\1_\2", value).lower()


def create_db_connection(path: str):
    """Creates the main database connection object

    Args:
        path: The path of the database (current or to be created)

    Returns:
        connection: A database connection object
    """
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("INFO:    Connection to DB successful")
    except sqlite3.Error as e:
        print(f"ERROR:   The error '{e}' occurred")

    return connection


def execute_db_query(connection, query: str) -> None:
    """Executes a SQL query on the Sqlite3 database

    Args:
        connection: A database connection object
        query: The SQL query as a string

    Returns:
        Nothing.
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")


def save_game_to_db(connection, pgn: dict) -> None:
    """Saves a Game to the Sqlite3 database

    Args:
        connection: A database connection object
        pgn: A PGN dictionary representation

    Returns:
        Nothing.
    """
    execute_db_query(
        connection,
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
    """Uses the chess.com API to fetch the requested users games.

    Args:
        user: A chess.com username

    Returns:
        list: A list of all games for that user.
    """
    req = requests.get(f"https://api.chess.com/pub/player/{user}/games/archives")
    archive_urls = req.json()["archives"]
    games_list = []

    for url in archive_urls:
        archived_games = requests.get(url).json()["games"]

        for game in archived_games:
            games_list.append(game)

    print(f"INFO:    Imported {len(games_list)} games from chess.com")
    return games_list


def fetch_lichess_org_games(user: str) -> list:
    """Uses the lichess API to fetch the requested users games.

    Args:
        user: A lichess username

    Returns:
        list: A list of all games for that user.
    """
    client = berserk.Client()
    req = client.games.export_by_player(user, as_pgn=True)
    games_list = list(req)

    print(f"INFO:    Imported {len(games_list)} games from lichess.org")
    return games_list


def build_pgn_dict(pgn: str) -> dict:
    """Takes any pgn text file and coverts to a dictionary object

    All pgn tags are converted to snake case. After converting, the dictionary
    is checked against a tuple of expected keys, and if missing, adds them with
    and empty string value. This ensures that each dictionary is uniform to
    match the database table.

    Args:
        pgn: A PGN string

    Returns:
        A Python Dictionary
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

    # If an expected key isn't present in the dictionary representation of the
    # pgn, then it is added with an empty string as its value.
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

    for key in expected_keys:
        if key not in game_dict:
            game_dict[key] = ""

    return game_dict


@click.group()
@click.option(
    "-u",
    "--user",
    help="You username for the chess site.",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
    help="Where you would like your database saved?",
)
@click.pass_context
def cli(ctx, user, output):
    """
    Save your chess games to an sqlite database.\n
    You can `fetch` your games from chess.com or lichess.org. You can also
    `save` local pgn files to the database.\n
    Type `pgn-to-sqlite --help` for more information.
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

    # Set the context to pass to commands.
    ctx.ensure_object(dict)
    ctx.obj["USER"] = user
    ctx.obj["OUTPUT"] = output
    ctx.obj["DB_CONN"] = db_conn


@cli.command()
@click.argument("site")
@click.pass_context
def fetch(ctx, site):
    """Fetch all games from the requested site."""

    user = ctx.obj["USER"]
    output = ctx.obj["OUTPUT"]
    db_conn = ctx.obj["DB_CONN"]

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
            f"'{site}' is not a valid argument. Check --help for valid inputs"
        )

    print(f"INFO:    Games saved to {output}")


@cli.command()
@click.argument("folder")
@click.pass_context
def save(ctx, folder):
    """Fetch all pgn file from the given folder."""

    output = ctx.obj["OUTPUT"]
    db_conn = ctx.obj["DB_CONN"]

    folder_path = Path(folder)

    print(f"INFO:    Fetching games from folder: {folder_path}")

    for pgn in folder_path.glob("*.pgn"):
        with pgn.open() as f:
            pgn_text = f.read()
            pgn_dict = build_pgn_dict(pgn_text)
            save_game_to_db(db_conn, pgn_dict)

    print(f"INFO:    Games saved to {output}")


if __name__ == "__main__":
    cli()
