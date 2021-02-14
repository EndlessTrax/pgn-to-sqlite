import pytest
import requests


@pytest.fixture()
def example_pgn() -> str:
    r = requests.get("https://api.chess.com/pub/player/endlesstrax/games/2021/02")
    return r.json()["games"][5]["pgn"]
