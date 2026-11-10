"""Manual Argon2 hashing check.

Run from the project root:
    python scripts/check_security.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from security import hash_password, verify_password  # noqa: E402


def main() -> None:
    password = "mysecret123"
    hashed = hash_password(password)

    print("Argon2 hash generated:", hashed.startswith("$argon2"))
    print("Correct password verifies:", verify_password(password, hashed))
    print("Wrong password verifies:", verify_password("wrong123", hashed))


if __name__ == "__main__":
    main()
