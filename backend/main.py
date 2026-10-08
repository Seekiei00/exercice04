"""Point d'entrée de l'API FastAPI."""

from fastapi import FastAPI

from backend.routers import analytics, auth, frequentations

app = FastAPI(
    title="Observatoire de fréquentation des médiathèques",
    description="Fréquentation publique paginée et bilan réservé aux analystes.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(frequentations.router)
app.include_router(analytics.router)


@app.get("/", tags=["Accueil"])
def root():
    return {
        "message": "API démarrée",
        "documentation": "/docs",
    }
