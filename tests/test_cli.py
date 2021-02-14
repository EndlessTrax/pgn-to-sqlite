from pgn_to_sqlite.cli import convert_to_snake_case, build_pgn_dict


def test_snake_case_conversion():
    result = convert_to_snake_case("SpamSpam")
    assert result == "spam_spam"


def test_build_png_dict(example_pgn):
    result = build_pgn_dict(example_pgn)
    assert result["white"] == "EndlessTrax"
    assert result["termination"] == "EndlessTrax won by resignation"
