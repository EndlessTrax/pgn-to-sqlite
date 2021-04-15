# PGN to Sqlite

[![PyPI version](https://badge.fury.io/py/pgn_to_sqlite.svg)](https://badge.fury.io/py/pgn_to_sqlite)
![GitHub](https://img.shields.io/github/license/endlesstrax/pgn-to-sqlite)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)

A cli application for pulling pgn files from Chess.com and Lichess.org and putting your games into a sqlite database.

## Install

> Requires Python 3.6 and above.

MacOS / Linux:

```bash
python3 -m pip install pgn_to_sqlite
```

Windows:

```powershell
python -m pip install pgn_to_sqlite
```

## Usage

The cli expects three arguments: `site`, `username`, and `output`.

`site`: can be with `chess` or `lichess`, for [chess.com](https://www.chess.com) and [lichess.org](https://lichess.org), respectively.

`-u username`: The username of the user you wish to download games of.

`-o output`: should be a `path` to the `sqlite3` database.

### Example

```powershell
pgn-to-sqlite lichess -u myusername -o data.db
```

> If you've played a lot of games, **be patient**, it could take a minute or two.

## Feedback and Contribution

If you find a bug, please file an [issue](https://github.com/EndlessTrax/pgn-to-sqlite/issues).

If you have feature requests, please [file an issue](https://github.com/EndlessTrax/pgn-to-sqlite/issues) and use the appropriate label.

Please **raise an issue before making a PR**, so that the issue and implementation can be discussed before you write any code. This will save you time, and increase the chances of your PR being merged without significant changes.

Please **format you code** with [Black](https://pypi.org/project/black/).

Please **include tests** for any PR's that include code (unless current tests cover your code contribution).

## Support

If you would like to show your support for the project, I would be very grateful if you would donate to a charity close to my heart, [Walk AS One](https://walkasone.org/donate).

And if you would prefer to donate to me personally instead, [you can sponsor me on Github](https://github.com/sponsors/EndlessTrax)? 🤓
