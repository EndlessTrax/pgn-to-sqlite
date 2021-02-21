import click
import requests
import berserk
import helpers


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
    """
    Which SITE do you want to download your games from?
    You can download games from chess.com or lichess.org.\n
    ARGS:    chess    OR     lichess
    """

    # TODO: Add check for if db exists.
    CONN = helpers.create_db_connection(output)
    helpers.create_games_table(CONN)

    if site == "chess":
        req = requests.get(f"https://api.chess.com/pub/player/{user}/games/archives")
        archive_urls = req.json()["archives"]

        for url in archive_urls:
            archived_games = requests.get(url).json()["games"]

            for game in archived_games:
                pgn = helpers.build_pgn_dict(game["pgn"])
                query = helpers.save_game_to_db(pgn)
                helpers.execute_query(CONN, query)

    elif site == "lichess":
        client = berserk.Client()
        req = client.games.export_by_player(user, as_pgn=True)
        games = list(req)

        for game in games:
            pgn = helpers.build_pgn_dict((game))
            query = helpers.save_game_to_db(pgn)
            helpers.execute_query(CONN, query)

    # Close DB connection before extiing the application
    CONN.close()


if __name__ == "__main__":
    main()
