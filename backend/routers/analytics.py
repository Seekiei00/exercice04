"""Bilan analytique réservé au rôle analyst."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import require_roles
from backend.models import Frequentation, User
from backend.schemas import BilanResponse

router = APIRouter(prefix="/analytics", tags=["Analyse"])


@router.get("/bilan", response_model=BilanResponse)
def bilan(
    # 401 sans token valide, 403 si le rôle n'est pas analyst.
    current_user: User = Depends(require_roles("analyst")),
    db: Session = Depends(get_db),
):
    """Calcule le bilan global à partir des observations en base."""

    nb_observations, total_visiteurs = db.execute(
        select(
            func.count(Frequentation.id),
            func.coalesce(func.sum(Frequentation.visiteurs), 0),
        )
    ).one()

    par_mediatheque = db.execute(
        select(
            Frequentation.mediatheque,
            func.sum(Frequentation.visiteurs),
        )
        .group_by(Frequentation.mediatheque)
        .order_by(Frequentation.mediatheque)
    ).all()

    moyenne = total_visiteurs / nb_observations if nb_observations else 0.0

    return {
        "nb_observations": nb_observations,
        "total_visiteurs": int(total_visiteurs),
        "moyenne_visiteurs": round(moyenne, 2),
        "par_mediatheque": [
            {"mediatheque": nom, "total_visiteurs": int(total)}
            for nom, total in par_mediatheque
        ],
    }
