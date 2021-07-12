import requests
from click.testing import CliRunner
from pgn_to_sqlite.cli import build_pgn_dict, convert_to_snake_case, cli


def test_snake_case_conversion():
    result = convert_to_snake_case("SpamSpam")
    assert result == "spam_spam"


def test_build_png_dict_from_chess_dotcom():
    with open("tests/game_files/test_pgn_file_chess_dotcom.pgn", "r") as f:
        pgn_str = f.read()
        result = build_pgn_dict(pgn_str)

    assert result["white"] == "EndlessTrax"
    assert result["termination"] == "EndlessTrax won by checkmate"


def test_build_png_dict_from_lichess():
    with open("tests/game_files/test_pgn_file_lichess.pgn", "r") as f:
        pgn_str = f.read()
        result = build_pgn_dict(pgn_str)

    assert result["black"] == "endlesstrax"
    assert result["opening"] == "Sicilian Defense: Old Sicilian"


def test_chess_dotcom_api_endpoint():
    r = requests.get(f"https://api.chess.com/pub/player/endlesstrax/games/archives")
    assert r.status_code == 200


def test_ValueError_on_invalid_args():
    runner = CliRunner()
    result = runner.invoke(
        cli, ["-u", "endlesstrax", "-o", "games.db", "fetch", "invaild"]
    )
    assert result.exit_code == 1


def test_folder_input_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["-o", "games.db", "save", "tests/game_files/"])
    assert result.exit_code == 0
