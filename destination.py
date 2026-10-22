import sqlite3
from contextlib import closing
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "destination.db"


def initialiser_destination():
    with closing(sqlite3.connect(DB_PATH)) as connexion:
        with connexion:
            connexion.execute("""
                CREATE TABLE IF NOT EXISTS produits (
                    id INTEGER PRIMARY KEY,
                    nom TEXT NOT NULL,
                    prix REAL NOT NULL CHECK (prix >= 0),
                    stock INTEGER NOT NULL CHECK (stock >= 0)
                )
            """)

def charger_produits(produits):
    with closing(sqlite3.connect(DB_PATH)) as connexion:
        with connexion:
            for produit_id, produit in produits.items():
                connexion.execute(
                    """
                    INSERT INTO produits (id, nom, prix, stock)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        nom = excluded.nom,
                        prix = excluded.prix,
                        stock = excluded.stock
                    """,
                    (
                        int(produit_id),
                        produit["nom"],
                        produit["prix"],
                        produit["stock"]
                    )
                )
def lire_destination():
    with closing(sqlite3.connect(DB_PATH)) as connexion:
        connexion.row_factory = sqlite3.Row
        lignes = connexion.execute(
            "SELECT id, nom, prix, stock FROM produits ORDER BY id"
        ).fetchall()

    return [dict(ligne) for ligne in lignes]

if __name__ == "__main__":
    initialiser_destination()
    print(lire_destination())