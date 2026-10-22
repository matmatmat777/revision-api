import destination
import sqlite3
import pytest

def test_upsert_produit(tmp_path, monkeypatch):
    monkeypatch.setattr(
        destination,
        "DB_PATH",
        tmp_path / "destination_test.db"
    )
    destination.initialiser_destination()

    # Premier chargement : insertion.
    destination.charger_produits({
        "1": {"nom": "Souris", "prix": 25, "stock": 3}
    })

    # Deuxième chargement : mise à jour du même identifiant.
    destination.charger_produits({
        "1": {"nom": "Souris", "prix": 35, "stock": 0}
    })

    assert destination.lire_destination() == [
        {"id": 1, "nom": "Souris", "prix": 35.0, "stock": 0}
    ]

def test_chargement_annule_si_erreur(tmp_path, monkeypatch):
    monkeypatch.setattr(
        destination,
        "DB_PATH",
        tmp_path / "destination_test.db"
    )
    destination.initialiser_destination()

    produits = {
        "1": {"nom": "Souris", "prix": 25, "stock": 3},
        "2": {"nom": "Clavier", "prix": -10, "stock": 2}
    }

    with pytest.raises(sqlite3.IntegrityError):
        destination.charger_produits(produits)

    assert destination.lire_destination() == []