"""Run one or more SQL files against data/chinook.duckdb, in the order given.

Usage: python src/run_sql.py sql/01_staging.sql [sql/02_quality.sql ...]

Files that contain only comments or are empty are skipped. Views created by
the SQL files are stored inside the DuckDB file.
"""
import sys
from pathlib import Path

import duckdb

DB_PATH = "data/chinook.duckdb"


def has_sql(text: str) -> bool:
    """True if the text contains anything besides blank lines and -- comments."""
    return any(line.strip() and not line.strip().startswith("--") for line in text.splitlines())


def main(files: list[str]) -> int:
    if not Path(DB_PATH).exists():
        print(f"{DB_PATH} not found. Run: make load")
        return 1
    con = duckdb.connect(DB_PATH)
    try:
        for name in files:
            text = Path(name).read_text()
            if not has_sql(text):
                print(f"{name}: no SQL yet, skipped")
                continue
            con.execute(text)
            print(f"{name}: ok")
    except duckdb.Error as err:
        print(f"{name}: SQL error\n{err}")
        return 1
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))