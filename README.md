# PGN to SQLite

![PyPI version](https://img.shields.io/pypi/v/pgn-to-sqlite)
![GitHub](https://img.shields.io/github/license/endlesstrax/pgn-to-sqlite)
![Python Version](https://img.shields.io/pypi/pyversions/pgn-to-sqlite)

A CLI application for pulling PGN files from Chess.com and Lichess.org and saving your games into a SQLite database.

It can also be used to save PGN files from a local folder to a SQLite database.

## Requirements

Python 3.10 or higher is required.

## Installation

It is recommended that you install this package in a virtual or isolated environment. The easiest way to do this is with [pipx](https://github.com/pypa/pipx):

```shell
pipx install pgn_to_sqlite
```

Alternatively, you can install it with `pip`:

```bash
pip install pgn_to_sqlite
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install pgn_to_sqlite
```

## Usage

```shell
Usage: pgn-to-sqlite [OPTIONS] COMMAND [ARGS]...

  Save your chess games to a SQLite database.

  You can `fetch` your games from chess.com or lichess.org. You can also
  `save` local PGN files to the database.

Options:
  -u, --user TEXT    Your username for the chess site.
  -o, --output FILE  Where you would like your database saved.  [required]
  --help             Show this message and exit.

Commands:
  fetch  Fetch all games from the requested site.
  save   Save all PGN files from the given folder.
```

### Fetching Games from Chess.com or Lichess.org

To download, parse, and save your games, both `--user` and `--output` are required. The `fetch` command accepts either `chess` or `lichess` as an argument for [Chess.com](https://www.chess.com) and [Lichess.org](https://lichess.org) respectively.

**Example:**

```shell
pgn-to-sqlite -u endlesstrax -o games.db fetch lichess
```

> **Note:** If you've played a lot of games, be patient—it could take a minute or two to download and process them all.

### Saving Games from a Local Folder

To save games from local PGN files to your database, only `--output` is required. The `save` command expects a folder path as an argument.

**Example:**

```shell
pgn-to-sqlite -o games.db save ./chess/games/
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and development workflows.

### Setting Up Your Development Environment

1. Install `uv` if you haven't already:
   ```bash
   pip install uv
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/EndlessTrax/pgn-to-sqlite.git
   cd pgn-to-sqlite
   ```

3. Sync dependencies and set up the virtual environment:
   ```bash
   uv sync
   ```

### Running Tests

Run the test suite with:

```bash
uv run pytest
```

For coverage reporting:

```bash
uv run pytest --cov
```

### Linting and Formatting

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

```bash
# Check for issues
uv run ruff check .

# Format code
uv run ruff format .
```

### Building the Project

To build the package:

```bash
uv build
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **File an issue first** - Before making a PR, please [file an issue](https://github.com/EndlessTrax/pgn-to-sqlite/issues) so the implementation can be discussed. This saves time and increases the chances of your PR being merged without significant changes.

2. **Lint and format your code** - Use `uv run ruff check .` and `uv run ruff format .` to ensure your code follows the project's style guidelines.

3. **Include tests** - Please include tests for any code changes (unless current tests already cover your contribution).

4. **Update documentation** - If your changes affect usage, please update the README accordingly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you find this project useful and would like to show your support, you can:
- [Sponsor on GitHub](https://github.com/sponsors/EndlessTrax)
- [Buy me a coffee](https://ko-fi.com/endlesstrax) ☕
