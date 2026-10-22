import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "produits.db"


def get_connection():
    connexion = sqlite3.connect(DB_PATH)
    connexion.row_factory = sqlite3.Row
    return connexion


def initialiser_base():
    with get_connection() as connexion:
        connexion.execute("""
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY,
                nom TEXT NOT NULL,
                prix REAL NOT NULL CHECK (prix >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
            )
        """)


if __name__ == "__main__":
    initialiser_base()