"""
Routeurs API pour la gestion des élèves.

Ce module définit les endpoints REST pour les opérations sur les élèves
et la génération des données.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.student import GenerationParams
from app.services.database_init import initialize_database
from app.services.student_service import get_all_students, get_students_count

router = APIRouter()


@router.post("/generate")
async def generate_data(
    params: GenerationParams,
    db: Session = Depends(get_db)
):
    """
    Génère les données des élèves de manière déterministe.

    Args:
        params: Paramètres de génération (chef_groupe, count)
        db: Session de base de données

    Returns:
        dict: Résumé de la génération avec statistiques

    Raises:
        HTTPException: Si une erreur survient lors de la génération
    """
    try:
        result = initialize_database(
            db,
            chef_groupe=params.chef_groupe,
            count=params.count
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


@router.get("/list")
async def list_students(
    db: Session = Depends(get_db)
):
    """
    Liste tous les élèves de la base de données.

    Args:
        db: Session de base de données

    Returns:
        dict: Liste des élèves avec nombre total
    """
    students = get_all_students(db)
    return {
        "total": len(students),
        "students": [s.to_dict() for s in students]
    }


@router.get("/count")
async def count_students(
    db: Session = Depends(get_db)
):
    """
    Retourne le nombre total d'élèves.

    Args:
        db: Session de base de données

    Returns:
        dict: Nombre d'élèves
    """
    return {"count": get_students_count(db)}
