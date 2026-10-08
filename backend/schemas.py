"""Schémas Pydantic utilisés par l'API."""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    """Inscription : le rôle n'est pas fourni par le client."""

    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    # bcrypt ne prend en compte que les 72 premiers octets.
    password: str = Field(min_length=8, max_length=72)


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
