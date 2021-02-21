import re
import berserk
import requests
from peewee import *


def convert_to_snake_case(value: str) -> str:
    """Convert any camal case attribute name to snake case"""
    return re.compile(r"(.)([A-Z][a-z]+)").sub(r"\1_\2", value).lower()


def build_pgn_dict(pgn: str) -> dict:
    """Takes any pgn text file and coverts to a dictonary object
    
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

        # The move notiation is a single line in the pgn.
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
        "utc_date",
        "utc_time",
        "white_elo",
        "black_elo",
        "variant",
        "time_control",
        "termination",
    )

    for key in expected_keys:
        if key not in game_dict:
            game_dict[key] = ""

    return game_dict


def save_game_to_db(Game, pgn: dict) -> None:
    """TODO:"""
    Game.create(
        event=pgn["event"],
        site=pgn["site"],
        date=pgn["date"],
        round=pgn["round"],
        white=pgn["white"],
        black=pgn["black"],
        result=pgn["result"],
        eco=pgn["eco"],
        utc_date=pgn["utc_date"],
        utc_time=pgn["utc_time"],
        white_elo=pgn["white_elo"],
        black_elo=pgn["black_elo"],
        variant=pgn["variant"],
        time_control=pgn["time_control"],
        termination=pgn["termination"],
    )


def fetch_chess_dotcom_games(user: str) -> list:
    """TODO:"""
    req = requests.get(f"https://api.chess.com/pub/player/{user}/games/archives")
    archive_urls = req.json()["archives"]

    for url in archive_urls:
        archived_games = requests.get(url).json()["games"]

    return archived_games


def fetch_lichess_org_games(user: str) -> list:
    """TODO:"""
    client = berserk.Client()
    req = client.games.export_by_player(user, as_pgn=True)
    games = list(req)

    return games
