import client_api


def test_valeur_stock():
    produits = {
        "1": {"nom": "Clavier", "prix": 30, "stock": 2},
        "2": {"nom": "Souris", "prix": 25, "stock": 3},
        "3": {"nom": "Écran", "prix": 150, "stock": 0}
    }

    assert client_api.valeur_stock(produits) == 135


def test_recuperation_pages(monkeypatch):
    urls_appelees = []

    pages = iter([
        {
            "1": {"nom": "Souris", "prix": 25, "stock": 3},
            "2": {"nom": "Clavier", "prix": 30, "stock": 0}
        },
        {
            "3": {"nom": "Écran", "prix": 150, "stock": 2}
        },
        {}
    ])

    def fausse_lire_page(url):
        urls_appelees.append(url)
        return next(pages)

    monkeypatch.setattr(
        client_api,
        "lire_page",
        fausse_lire_page
    )

    produits = client_api.recuperer_tous_les_produits()

    assert set(produits) == {"1", "2", "3"}
    assert len(urls_appelees) == 3
    assert urls_appelees == [
        "http://127.0.0.1:8000/produits?limit=2&offset=0",
        "http://127.0.0.1:8000/produits?limit=2&offset=2",
        "http://127.0.0.1:8000/produits?limit=2&offset=4"
    ]