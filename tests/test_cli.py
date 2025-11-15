import os
import sqlite3
import tempfile
from unittest.mock import Mock, patch

import click
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


def test_chess_dotcom_connection_error():
    """Test that ConnectionError is properly handled for chess.com API."""
    with patch("pgn_to_sqlite.cli.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        with pytest.raises(click.exceptions.Abort):
            fetch_chess_dotcom_games("testuser")


def test_chess_dotcom_timeout_error():
    """Test that Timeout error is properly handled for chess.com API."""
    with patch("pgn_to_sqlite.cli.requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        with pytest.raises(click.exceptions.Abort):
            fetch_chess_dotcom_games("testuser")


def test_chess_dotcom_404_error():
    """Test that 404 error (user not found) is properly handled for chess.com API."""
    with patch("pgn_to_sqlite.cli.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        with pytest.raises(click.exceptions.Abort):
            fetch_chess_dotcom_games("nonexistentuser")


def test_chess_dotcom_429_error():
    """Test that 429 error (rate limit) is properly handled for chess.com API."""
    with patch("pgn_to_sqlite.cli.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response

        with pytest.raises(click.exceptions.Abort):
            fetch_chess_dotcom_games("testuser")


def test_chess_dotcom_invalid_json():
    """Test that invalid JSON response is properly handled for chess.com API."""
    with patch("pgn_to_sqlite.cli.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        with pytest.raises(click.exceptions.Abort):
            fetch_chess_dotcom_games("testuser")


def test_chess_dotcom_missing_archives_key():
    """Test that missing 'archives' key in response is properly handled."""
    with patch("pgn_to_sqlite.cli.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}  # Missing 'archives' key
        mock_get.return_value = mock_response

        with pytest.raises(click.exceptions.Abort):
            fetch_chess_dotcom_games("testuser")


def test_chess_dotcom_archive_fetch_failure_continues():
    """Test that failures in fetching individual archives don't stop the process."""
    with patch("pgn_to_sqlite.cli.requests.get") as mock_get:
        # First call returns archive list
        archive_list_response = Mock()
        archive_list_response.status_code = 200
        archive_list_response.raise_for_status.return_value = None
        archive_list_response.json.return_value = {
            "archives": ["https://api.chess.com/pub/player/test/games/2023/01"]
        }

        # Second call (for archive) fails
        mock_get.side_effect = [
            archive_list_response,
            requests.exceptions.ConnectionError("Network error"),
        ]

        # Should not raise, but return empty list
        result = fetch_chess_dotcom_games("testuser")
        assert result == []


def test_lichess_connection_error():
    """Test that ConnectionError is properly handled for lichess.org API."""
    with patch("pgn_to_sqlite.cli.berserk.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.games.export_by_player.side_effect = (
            requests.exceptions.ConnectionError("Network error")
        )

        with pytest.raises(click.exceptions.Abort):
            fetch_lichess_org_games("testuser")


def test_lichess_timeout_error():
    """Test that Timeout error is properly handled for lichess.org API."""
    with patch("pgn_to_sqlite.cli.berserk.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.games.export_by_player.side_effect = requests.exceptions.Timeout(
            "Request timeout"
        )

        with pytest.raises(click.exceptions.Abort):
            fetch_lichess_org_games("testuser")


def test_lichess_404_error():
    """Test that 404 error (user not found) is properly handled for lichess.org API."""
    with patch("pgn_to_sqlite.cli.berserk.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_response = Mock()
        mock_response.status_code = 404
        error = requests.exceptions.HTTPError(response=mock_response)
        error.response = mock_response
        mock_instance.games.export_by_player.side_effect = error

        with pytest.raises(click.exceptions.Abort):
            fetch_lichess_org_games("nonexistentuser")


def test_lichess_429_error():
    """Test that 429 error (rate limit) is properly handled for lichess.org API."""
    with patch("pgn_to_sqlite.cli.berserk.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_response = Mock()
        mock_response.status_code = 429
        error = requests.exceptions.HTTPError(response=mock_response)
        error.response = mock_response
        mock_instance.games.export_by_player.side_effect = error

        with pytest.raises(click.exceptions.Abort):
            fetch_lichess_org_games("testuser")


def test_lichess_unexpected_error():
    """Test that unexpected errors are properly handled for lichess.org API."""
    with patch("pgn_to_sqlite.cli.berserk.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.games.export_by_player.side_effect = Exception("Unexpected error")

        with pytest.raises(click.exceptions.Abort):
            fetch_lichess_org_games("testuser")


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
