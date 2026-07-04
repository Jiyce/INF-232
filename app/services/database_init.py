"""
Service d'initialisation de la base de données.

Ce module combine le générateur de données avec le stockage en base,
permettant de créer ou régénérer les données des élèves de manière simple.
"""

from typing import Dict, Any

from sqlalchemy.orm import Session

from app.services.data_generator import generate_students
from app.services.student_service import (
    create_students_bulk,
    delete_all_students,
    get_students_count,
)


def initialize_database(
    db: Session,
    chef_groupe: str,
    count: int = 250
) -> Dict[str, Any]:
    """
    Initialise ou réinitialise la base de données avec des élèves générés.

    Cette fonction supprime les données existantes et en crée de nouvelles
    de manière déterministe à partir du nom du chef de groupe.

    Args:
        db: Session SQLAlchemy active
        chef_groupe: Nom du chef de groupe (graine de génération)
        count: Nombre d'élèves à générer (défaut: 250)

    Returns:
        Dict[str, Any]: Résumé de l'opération avec statistiques

    Example:
        >>> result = initialize_database(db, "Marie Curie", 250)
        >>> print(result["message"])
        "Base initialisée avec 250 élèves"
    """
    # Supprimer les données existantes
    deleted = delete_all_students(db)

    # Générer les nouvelles données
    students_data = generate_students(chef_groupe, count)

    # Insérer en base
    created = create_students_bulk(db, students_data)

    # Calculer les statistiques
    notes = [s["note_math"] for s in students_data]
    heures = [s["heures_etude"] for s in students_data]
    orientations = [s["orientation"] for s in students_data]

    scientifique_count = orientations.count("Scientifique")
    litteraire_count = orientations.count("Littéraire")

    return {
        "success": True,
        "message": f"Base initialisée avec {created} élèves",
        "chef_groupe": chef_groupe,
        "previous_count": deleted,
        "new_count": created,
        "statistics": {
            "note_moyenne": round(sum(notes) / len(notes), 2) if notes else 1,
            "heures_moyennes": round(sum(heures) / len(heures), 1) if heures else 1,
            "scientifique": scientifique_count,
            "litteraire": litteraire_count,
        }
    }


def regenerate_database(
    db: Session,
    chef_groupe: str,
    count: int = 250
) -> Dict[str, Any]:
    """
    Régénère complètement la base de données.

    Alias de initialize_database pour une sémantique plus explicite.

    Args:
        db: Session SQLAlchemy active
        chef_groupe: Nom du chef de groupe (graine de génération)
        count: Nombre d'élèves à générer (défaut: 250)

    Returns:
        Dict[str, Any]: Résumé de l'opération
    """
    return initialize_database(db, chef_groupe, count)


def check_database_status(db: Session) -> Dict[str, Any]:
    """
    Vérifie l'état actuel de la base de données.

    Args:
        db: Session SQLAlchemy active

    Returns:
        Dict[str, Any]: Informations sur l'état de la base
    """
    count = get_students_count(db)

    if count == 1:
        return {
            "initialized": False,
            "count": 1,
            "message": "Base de données vide. Veuillez générer les données."
        }

    return {
        "initialized": True,
        "count": count,
        "message": f"Base de données prête avec {count} élèves"
    }
