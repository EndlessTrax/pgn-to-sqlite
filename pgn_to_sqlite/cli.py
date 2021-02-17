import re
import click
import requests
import berserk


CHESS_DOTCOM_ARCHIVES_URL = "https://api.chess.com/pub/player/{}/games/archives"
LICHESS_GAMES_URL = "https://lichess.org/api/games/user/{}"


def convert_to_snake_case(value: str) -> str:
    """"""
    return re.compile(r"(.)([A-Z][a-z]+)").sub(r"\1_\2", value).lower()


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
    prompt="Output path of the database...",
    help="Where you would like your database saved?",
)
def main(site, user, output):
    """"""

    if site == "chess":
        r = requests.get(CHESS_DOTCOM_ARCHIVES_URL.format(user))
        archive_urls = r.json()["archives"]

        for url in archive_urls:
            archived_games = requests.get(url).json()["games"]

            for game in archived_games:
                print(build_pgn_dict(game["pgn"]))

    elif site == "lichess":
        client = berserk.Client()
        r = client.games.export_by_player(user, as_pgn=True)
        games = list(r)

        for game in games:
            print(build_pgn_dict((game)))


if __name__ == "__main__":
    main()
