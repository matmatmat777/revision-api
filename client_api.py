import csv
import json
import logging
import time
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from destination import charger_produits, initialiser_destination


logger = logging.getLogger(__name__)


def lire_page(url):
    for tentative in range(1, 4):
        try:
            with urlopen(url, timeout=10) as reponse:
                return json.load(reponse)

        except HTTPError:
            raise

        except URLError:
            if tentative == 3:
                raise

            logger.warning(
                "Connexion impossible, essai %s/3. "
                "Nouvelle tentative dans 2 secondes...",
                tentative
            )
            time.sleep(2)


def recuperer_tous_les_produits():
    base_url = "http://127.0.0.1:8000/produits"
    limit = 2
    offset = 0
    tous_les_produits = {}

    while True:
        parametres = urlencode({
            "limit": limit,
            "offset": offset
        })

        url = f"{base_url}?{parametres}"
        produits = lire_page(url)

        logger.info(
            "offset=%s : %s produit(s) reçu(s)",
            offset,
            len(produits)
        )

        if not produits:
            break

        tous_les_produits.update(produits)
        offset += limit

    return tous_les_produits


def afficher_produits(produits):
    for produit_id, produit in produits.items():
        print(
            f"{produit_id} — {produit['nom']} : "
            f"{produit['prix']:.2f} € — "
            f"stock : {produit['stock']}"
        )

    print(f"Total : {len(produits)} produit(s)")


def exporter_csv(produits):
    chemin = Path(__file__).resolve().parent / "produits_export.csv"

    with chemin.open("w", newline="", encoding="utf-8") as fichier:
        colonnes = ["id", "nom", "prix", "stock"]
        writer = csv.DictWriter(fichier, fieldnames=colonnes)

        writer.writeheader()

        for produit_id, produit in produits.items():
            writer.writerow({
                "id": produit_id,
                "nom": produit["nom"],
                "prix": produit["prix"],
                "stock": produit["stock"]
            })

    return chemin


def valeur_stock(produits):
    total = 0

    for produit in produits.values():
        total += produit["stock"] * produit["prix"]

    return total


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    try:
        produits = recuperer_tous_les_produits()
    except HTTPError as erreur:
        logger.error("Erreur HTTP : %s", erreur.code)
        sys.exit(1)
    except URLError as erreur:
        logger.error("API inaccessible : %s", erreur.reason)
        sys.exit(1)
    else:
        afficher_produits(produits)
        valeur = valeur_stock(produits)
        print(f"Valeur totale du stock : {valeur:.2f} €")
        chemin = exporter_csv(produits)
        logger.info("Export créé : %s", chemin)

        initialiser_destination()
        charger_produits(produits)
        logger.info("Chargement SQLite terminé")