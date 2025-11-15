import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
import requests
from click.testing import CliRunner

from pgn_to_sqlite.cli import (
    build_pgn_dict,
    cli,
    convert_to_snake_case,
    fetch_chess_dotcom_games,
    fetch_lichess_org_games,
)


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


@pytest.mark.network
def test_chess_dotcom_api_endpoint():
    r = requests.get(
        "https://api.chess.com/pub/player/everydayronin/games/archives",
        headers={"User-Agent": "test@gmail.com"},
    )
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


def test_save_command_creates_database_with_games():
    """Test that save command with progress indicators saves all games correctly"""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_games.db")
        result = runner.invoke(cli, ["-o", db_path, "save", "tests/game_files/"])
        assert result.exit_code == 0

        # Verify the database was created and games were saved
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM games")
        count = cursor.fetchone()[0]
        conn.close()

        # We have 2 PGN files in the test directory
        assert count == 2
