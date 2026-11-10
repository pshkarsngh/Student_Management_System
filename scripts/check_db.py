"""Manual PostgreSQL connectivity check.

Run from the project root:
    python scripts/check_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text  # noqa: E402

from database import engine  # noqa: E402


def main() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - diagnostic script
        # Only print the exception type; never print the connection URL.
        print(f"Database connection failed: {type(exc).__name__}")
        raise SystemExit(1) from None

    print("PostgreSQL connected successfully!")


if __name__ == "__main__":
    main()
