import click
from peewee import *

from helpers import (
    fetch_chess_dotcom_games,
    fetch_lichess_org_games,
    build_pgn_dict,
    save_game_to_db,
)


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

    db = SqliteDatabase(output)

    class Game(Model):
        """Main Game model

        All field are currently strings. May change in the future and convert
        some to native data structures
        """

        event = CharField()
        site = CharField()
        date = CharField()
        round = CharField()
        white = CharField()
        black = CharField()
        result = CharField()
        eco = CharField()
        utc_date = CharField()
        utc_time = CharField()
        white_elo = CharField()
        black_elo = CharField()
        variant = CharField()
        time_control = CharField()
        termination = CharField()

        class Meta:
            database = db

    db.connect()
    db.create_tables([Game])

    if site == "chess":
        games = fetch_chess_dotcom_games(user)
        for game in games:
            pgn = build_pgn_dict(game["pgn"])
            save_game_to_db(Game, pgn)

    elif site == "lichess":
        games = fetch_lichess_org_games(user)
        for game in games:
            pgn = build_pgn_dict(game)
            save_game_to_db(Game, pgn)

    else:
        raise ValueError("That is not a valid site name. Check --help for valid inputs")


if __name__ == "__main__":
    main()
