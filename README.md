# PGN to Sqlite

![PyPI version](https://img.shields.io/pypi/v/pgn-to-sqlite)
![GitHub](https://img.shields.io/github/license/endlesstrax/pgn-to-sqlite)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

A cli application for pulling pgn files from Chess.com and Lichess.org and putting your games into a sqlite database.

## Install

> Requires Python 3.7 and above.

MacOS / Linux:

```bash
python3 -m pip install pgn_to_sqlite
```

Windows:

```powershell
python -m pip install pgn_to_sqlite
```

## Usage

```shell
Usage: pgn-to-sqlite [OPTIONS] COMMAND [ARGS]...

  Save your chess games to an sqlite database.

  You can `fetch` your games from chess.com or lichess.org. You can also
  `save` local pgn files to the database.

  Type `pgn-to-sqlite --help` for more information.

Options:
  -u, --user TEXT    You username for the chess site.
  -o, --output FILE  Where you would like your database saved?  [required]
  --help             Show this message and exit.

Commands:
  fetch  Fetch all games from the requested site.
  save   Fetch all pgn file from the given folder.
```

### Fetch games from chess.com or lichess.org

`username` and `output` are required when using `fetch` to download, parse, and save your games to your database. `fetch` accepts with `chess` or `lichess` as an argument for _[chess.com](https://www.chess.com)_ and _[lichess.org](https://lichess.org)_ respectively.

Example:

```shell
pgn-to-sqlite -u endlesstrax -o data.db fetch lichess
```

> If you've played a lot of games, **be patient**, it could take a minute or two.

### Save games from local folder

`output` is required when saving games from local pgn files to your database. `save` expects a folder path as an argument.

Example:

```shell
pgn-to-sqlite -o data.db save .\chess\games\
```

## Feedback and Contribution

If you find a bug, please file an [issue](https://github.com/EndlessTrax/pgn-to-sqlite/issues).

If you have feature requests, please [file an issue](https://github.com/EndlessTrax/pgn-to-sqlite/issues) and use the appropriate label.

Please **raise an issue before making a PR**, so that the issue and implementation can be discussed before you write any code. This will save you time, and increase the chances of your PR being merged without significant changes.

Please **format you code** with [Black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/).

Please **include tests** for any PR's that include code (unless current tests cover your code contribution).

## Support

If you would like to show your support for the project, I would be very grateful if you would donate to a charity close to my heart, [Walk AS One](https://walkasone.org/donate).

And if you would prefer to donate to me personally instead, [you can sponsor me on Github](https://github.com/sponsors/EndlessTrax)? 🤓
