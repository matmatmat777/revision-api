from fastapi.testclient import TestClient
from main import app
import pytest
import database

@pytest.fixture
def base_temporaire(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DB_PATH",
        tmp_path / "test_produits.db"
    )
    
@pytest.fixture
def client(base_temporaire):
    with TestClient(app) as client_test:
        yield client_test


def test_statut(client):
    reponse = client.get("/statut")

    assert reponse.status_code == 200
    assert reponse.json() == {"statut": "ok"}


def test_prix_negatif(client):

    reponse = client.post(
        "/produits/99",
        json={"nom": "Souris", "prix": -5}
    )

    assert reponse.status_code == 422
    assert client.get("/produits/99").status_code == 404


def test_ajout_produit(client):
    # Créer le produit.
    reponse = client.post(
        "/produits/100",
        json={"nom": "Clavier", "prix": 30, "stock": 5}
    )
    assert reponse.status_code == 201

    # Vérifier les données enregistrées.
    lecture = client.get("/produits/100")
    assert lecture.status_code == 200
    assert lecture.json() == {
        "nom": "Clavier",
        "prix": 30.0,
        "stock": 5
    }

    # Vérifier le stock et la disponibilité.
    stock = client.get("/produits/100/stock")
    assert stock.status_code == 200
    assert stock.json() == {
        "stock": 5,
        "disponible": True
    }

    # Essayer de créer un doublon.
    doublon = client.post(
        "/produits/100",
        json={"nom": "Autre clavier", "prix": 99, "stock": 0}
    )
    assert doublon.status_code == 409

    # Vérifier que le produit initial reste inchangé.
    lecture = client.get("/produits/100")
    assert lecture.json() == {
        "nom": "Clavier",
        "prix": 30.0,
        "stock": 5
    }

    # Modifier le produit.
    modification = client.put(
        "/produits/100",
        json={"nom": "Clavier mécanique", "prix": 50, "stock": 0}
    )
    assert modification.status_code == 200

    lecture = client.get("/produits/100")
    assert lecture.json() == {
        "nom": "Clavier mécanique",
        "prix": 50.0,
        "stock": 0
    }

    # Tester la suppression.
    suppression = client.delete("/produits/100")
    assert suppression.status_code == 200

    lecture = client.get("/produits/100")
    assert lecture.status_code == 404


def test_modifier_produit_inexistant(client):
    reponse = client.put(
        "/produits/999",
        json={"nom": "Clavier", "prix": 30, "stock": 5}
    )

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Produit introuvable"}

    lecture = client.get("/produits/999")
    assert lecture.status_code == 404


def test_stock_zero(client):
    client.post(
        "/produits/1",
        json={"nom": "Souris", "prix": 25, "stock": 0}
    )

    reponse = client.get("/produits/1/stock")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "stock": 0,
        "disponible": False
    }


def test_supprimer_produit_inexistant(client):
    reponse = client.delete("/produits/999")

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Produit introuvable"}


def test_lire_produit_inexistant(client):
    reponse = client.get("/produits/999")

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Produit introuvable"}


def test_liste_produits_vide(client):
    reponse = client.get("/produits")

    assert reponse.status_code == 200
    assert reponse.json() == {}


def test_nombre_produits_vide(client):
    reponse = client.get("/nombre-produits")

    assert reponse.status_code == 200
    assert reponse.json() == {"nombre": 0}


def test_resume_produit(client):
    creation = client.post(
        "/produits/1",
        json={"nom": "Souris", "prix": 25, "stock": 0}
    )
    assert creation.status_code == 201

    reponse = client.get("/produits/1/resume")

    assert reponse.status_code == 200
    assert reponse.json() == {
        "nom": "Souris",
        "disponible": False
    }


def test_prix_produit(client):
    # Préparer : créer le produit.
    creation = client.post(
        "/produits/1",
        json={"nom": "Écran", "prix": 150, "stock": 2}
    )
    assert creation.status_code == 201

    # Agir : demander son prix.
    reponse = client.get("/produits/1/prix")

    # Vérifier la réponse.
    assert reponse.status_code == 200
    assert reponse.json() == {"prix": 150.0}


def test_resume_produit_inexistant(client):
    reponse = client.get("/produits/999/resume")

    assert reponse.status_code == 404
    assert reponse.json() == {"detail": "Produit introuvable"}


def test_nom_vide(client):
    reponse = client.post(
        "/produits/1",
        json={"nom": "", "prix": 25, "stock": 3}
    )

    assert reponse.status_code == 422

    # Le produit invalide ne doit pas avoir été enregistré.
    lecture = client.get("/produits/1")
    assert lecture.status_code == 404


def test_nom_espaces(client):
    reponse = client.post(
        "/produits/1",
        json={"nom": "   ", "prix": 25, "stock": 3}
    )

    assert reponse.status_code == 422
    assert client.get("/produits/1").status_code == 404


def test_nom_nettoye(client):
    creation = client.post(
        "/produits/1",
        json={"nom": "  Souris  ", "prix": 25, "stock": 3}
    )

    assert creation.status_code == 201
    assert creation.json()["nom"] == "Souris"

    lecture = client.get("/produits/1")

    assert lecture.status_code == 200
    assert lecture.json()["nom"] == "Souris"


def test_champ_inconnu(client):
    reponse = client.post(
        "/produits/1",
        json={"nom": "Souris", "prix": 25, "stok": 3}
    )

    assert reponse.status_code == 422
    assert client.get("/produits/1").status_code == 404


def test_stock_par_defaut(client):
    reponse = client.post(
        "/produits/1",
        json={"nom": "Clavier", "prix": 30}
    )

    assert reponse.status_code == 201
    assert reponse.json()["stock"] == 0

    lecture = client.get("/produits/1")
    assert lecture.status_code == 200
    assert lecture.json()["stock"] == 0


def test_filtrer_produits_disponibles(client):
    client.post(
        "/produits/1",
        json={"nom": "Souris", "prix": 25, "stock": 3}
    )
    client.post(
        "/produits/2",
        json={"nom": "Clavier", "prix": 30, "stock": 0}
    )

    reponse = client.get(
        "/produits",
        params={"disponible": "true"}
    )

    assert reponse.status_code == 200
    assert reponse.json() == {
        "1": {
            "nom": "Souris",
            "prix": 25.0,
            "stock": 3
        }
    }


def test_filtrer_produits_indisponibles(client):
    client.post(
        "/produits/1",
        json={"nom": "Souris", "prix": 25, "stock": 3}
    )
    client.post(
        "/produits/2",
        json={"nom": "Clavier", "prix": 30, "stock": 0}
    )

    reponse = client.get(
        "/produits",
        params={"disponible": "false"}
    )

    assert reponse.status_code == 200
    assert reponse.json() == {
        "2": {
            "nom": "Clavier",
            "prix": 30.0,
            "stock": 0
        }
    }


def test_liste_sans_filtre(client):
    client.post(
        "/produits/1",
        json={"nom": "Souris", "prix": 25, "stock": 3}
    )
    client.post(
        "/produits/2",
        json={"nom": "Clavier", "prix": 30, "stock": 0}
    )

    reponse = client.get("/produits")

    assert reponse.status_code == 200
    assert set(reponse.json()) == {"1", "2"}


def test_pagination_produits(client):
    for produit_id in range(1, 4):
        creation = client.post(
            f"/produits/{produit_id}",
            json={
                "nom": f"Produit {produit_id}",
                "prix": 10,
                "stock": 1
            }
        )
        assert creation.status_code == 201

    reponse = client.get(
        "/produits",
        params={"limit": 1, "offset": 1}
    )

    assert reponse.status_code == 200
    assert reponse.json() == {
        "2": {
            "nom": "Produit 2",
            "prix": 10.0,
            "stock": 1
        }
    }


@pytest.mark.parametrize(
    "parametres",
    [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
        {"limit": "bonjour"},
    ]
)
def test_pagination_invalide(client, parametres):
    reponse = client.get("/produits", params=parametres)

    assert reponse.status_code == 422