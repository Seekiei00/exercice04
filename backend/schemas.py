"""Schémas Pydantic utilisés par l'API."""

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class FrequentationResponse(BaseModel):
    """Représentation d'une observation retournée par l'API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    mediatheque: str
    mois: str
    visiteurs: int


class PaginatedFrequentationsResponse(BaseModel):
    """Structure d'une réponse paginée."""

    items: list[FrequentationResponse]

    # Informations nécessaires au client pour construire sa navigation.
    page: int
    page_size: int
    total: int
    pages: int


class BilanMediatheque(BaseModel):
    """Sous-total d'une médiathèque."""

    mediatheque: str
    total_visiteurs: int


class BilanResponse(BaseModel):
    """Bilan global calculé sur les observations en base."""

    nb_observations: int
    total_visiteurs: int
    moyenne_visiteurs: float
    par_mediatheque: list[BilanMediatheque]
