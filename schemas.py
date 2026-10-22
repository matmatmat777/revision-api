from pydantic import BaseModel, ConfigDict, Field


class Produit(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    nom: str = Field(min_length=1)
    prix: float = Field(ge=0)
    stock: int = Field(ge=0, default=0)


class EtatStock(BaseModel):
    stock: int
    disponible: bool


class PrixProduit(BaseModel):
    prix: float = Field(ge=0)

    