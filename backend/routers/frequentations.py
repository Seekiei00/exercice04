"""Consultation publique et paginée des fréquentations."""

import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Frequentation
from backend.schemas import PaginatedFrequentationsResponse

router = APIRouter(prefix="/frequentations", tags=["Fréquentations"])


@router.get("", response_model=PaginatedFrequentationsResponse)
def list_frequentations(
    # Bornes validées par FastAPI : sinon réponse 422.
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Retourne une page d'observations, sans authentification."""

    total = db.scalar(select(func.count(Frequentation.id))) or 0

    # Ordre stable : mois, médiathèque, puis id pour départager.
    items = db.scalars(
        select(Frequentation)
        .order_by(
            Frequentation.mois,
            Frequentation.mediatheque,
            Frequentation.id,
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()

    # Une page au-delà des résultats renvoie simplement items: [].
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": math.ceil(total / page_size),
    }
