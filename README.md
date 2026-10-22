# API de produits et pipeline Python

Projet pratique de révision Python et Data Engineering : une API FastAPI
avec stockage SQLite, accompagnée d'un client d'extraction et de chargement.

## Fonctionnalités

- Création, lecture, modification et suppression de produits.
- Validation des données avec Pydantic.
- Filtrage par disponibilité et pagination avec limit/offset.
- Stockage persistant dans SQLite.
- Client Python qui parcourt toutes les pages de l'API.
- Export CSV et chargement dans une base SQLite de destination.
- Upsert par identifiant pour éviter les doublons.
- Transaction pour annuler le chargement en cas d'erreur.
- Logs et trois tentatives en cas d'erreur de connexion.
- Code de sortie non nul en cas d'échec HTTP ou de connexion.

## Installation

Projet développé et testé avec Python 3.14.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer l'API

```bash
uvicorn main:app --reload
```

Documentation interactive : http://127.0.0.1:8000/docs

La table des produits est créée automatiquement au démarrage.

## Exécuter le pipeline

Avec l'API lancée, dans un autre terminal :

```bash
source .venv/bin/activate
python client_api.py
```

Le pipeline récupère tous les produits et génère :

- `produits_export.csv` : export remplacé à chaque exécution.
- `destination.db` : base de destination alimentée par upsert.

Les bases et les exports locaux ne sont pas versionnés.

## Tests

```bash
pytest -q
```

Les tests utilisent des bases temporaires. Le test de pagination du client
simule les réponses sans appeler le réseau.

## Organisation

| Fichier | Rôle |
|---|---|
| main.py | Routes FastAPI et démarrage |
| schemas.py | Modèles et validation Pydantic |
| database.py | Connexion et initialisation de la base source |
| repository.py | Requêtes SQL de l'API |
| client_api.py | Extraction, pagination, export et lancement du chargement |
| destination.py | Initialisation, upsert et lecture de la destination |
| test_main.py | Tests de l'API |
| test_client.py | Tests du client et du calcul de valeur du stock |
| test_destination.py | Tests de l'upsert et du rollback |

## Limites connues

- Les suppressions dans la source ne sont pas répercutées en destination.
- La pagination par offset suppose une source stable pendant l'extraction.
- Les erreurs HTTP ne sont pas réessayées.
- Les logs sont affichés dans le terminal.
- L'API est destinée à un usage local pédagogique et ne possède pas
  d'authentification.
