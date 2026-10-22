import sqlite3
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query

from database import initialiser_base
from repository import (
    chercher_produit,
    chercher_tous_produits,
    effacer_produit,
    inserer_produit,
    modifier_produit,
    nombre_produits,
)
from schemas import EtatStock, PrixProduit, Produit


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialiser_base()
    yield


app = FastAPI(lifespan=lifespan)


def recuperer_produit(produit_id: int):
    produit = chercher_produit(produit_id)

    if produit is None:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable"
        )

    return produit


@app.get("/statut")
def statut():
    return {"statut": "ok"}


@app.post("/produits/{produit_id}", status_code=201)
def ajouter_produit(produit_id: int, produit: Produit):
    try:
        inserer_produit(
            produit_id,
            produit.nom,
            produit.prix,
            produit.stock
        )
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Cet identifiant existe déjà"
        )

    return produit.model_dump()


@app.get("/produits")
def lister_produits(
    disponible: bool | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    return chercher_tous_produits(disponible, limit, offset)


@app.get("/produits/{produit_id}")
def lire_produit(produit: dict = Depends(recuperer_produit)):
    return produit


@app.get("/produits/{produit_id}/stock", response_model=EtatStock)
def lire_stock(produit: dict = Depends(recuperer_produit)):
    return {
        "stock": produit["stock"],
        "disponible": produit["stock"] > 0
    }


@app.get("/produits/{produit_id}/prix", response_model=PrixProduit)
def lire_prix(produit: dict = Depends(recuperer_produit)):
    return {"prix": produit["prix"]}


@app.get("/nombre-produits")
def compter_produits():
    return {"nombre": nombre_produits()}


@app.get("/produits/{produit_id}/resume")
def verifier_produit(produit: dict = Depends(recuperer_produit)):
    return {
        "nom": produit["nom"],
        "disponible": produit["stock"] > 0
    }


@app.put("/produits/{produit_id}")
def remplacer_produit(produit_id: int, produit: Produit):
    modifie = modifier_produit(
        produit_id,
        produit.nom,
        produit.prix,
        produit.stock
    )

    if not modifie:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable"
        )

    return produit.model_dump()


@app.delete("/produits/{produit_id}")
def supprimer_produit(produit_id: int):
    supprime = effacer_produit(produit_id)

    if not supprime:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable"
        )

    return {"message": "Produit supprimé"}