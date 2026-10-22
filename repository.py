from contextlib import closing

from database import get_connection


def chercher_produit(produit_id: int):
    with closing(get_connection()) as connexion:
        ligne = connexion.execute(
            "SELECT nom, prix, stock FROM produits WHERE id = ?",
            (produit_id,)
        ).fetchone()

    if ligne is None:
        return None

    return dict(ligne)


def nombre_produits():
    with closing(get_connection()) as connexion:
        ligne = connexion.execute(
            "SELECT COUNT(*) AS nombre FROM produits"
        ).fetchone()

    return ligne["nombre"]


def chercher_tous_produits(
    disponible: bool | None = None,
    limit: int = 10,
    offset: int = 0
):
    requete = "SELECT id, nom, prix, stock FROM produits"

    if disponible is True:
        requete += " WHERE stock > 0"
    elif disponible is False:
        requete += " WHERE stock = 0"

    requete += " ORDER BY id LIMIT ? OFFSET ?"

    with closing(get_connection()) as connexion:
        lignes = connexion.execute(
            requete,
            (limit, offset)
        ).fetchall()

    return {
        ligne["id"]: {
            "nom": ligne["nom"],
            "prix": ligne["prix"],
            "stock": ligne["stock"]
        }
        for ligne in lignes
    }


def inserer_produit(produit_id: int, nom: str, prix: float, stock: int):
    with closing(get_connection()) as connexion:
        with connexion:
            connexion.execute(
                """
                INSERT INTO produits (id, nom, prix, stock)
                VALUES (?, ?, ?, ?)
                """,
                (produit_id, nom, prix, stock)
            )


def modifier_produit(produit_id: int, nom: str, prix: float, stock: int):
    with closing(get_connection()) as connexion:
        with connexion:
            curseur = connexion.execute(
                """
                UPDATE produits
                SET nom = ?, prix = ?, stock = ?
                WHERE id = ?
                """,
                (nom, prix, stock, produit_id)
            )

    return curseur.rowcount > 0


def effacer_produit(produit_id: int):
    with closing(get_connection()) as connexion:
        with connexion:
            curseur = connexion.execute(
                "DELETE FROM produits WHERE id = ?",
                (produit_id,)
            )

    return curseur.rowcount > 0