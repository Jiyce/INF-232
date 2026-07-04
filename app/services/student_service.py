"""
Service de gestion des élèves dans la base de données.

Ce module fournit les fonctions CRUD (Create, Read, Update, Delete)
pour manipuler les données des élèves via SQLAlchemy.
"""

from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.student import Student


def get_all_students(db: Session) -> List[Student]:
    """
    Récupère tous les élèves de la base de données.

    Args:
        db: Session SQLAlchemy active

    Returns:
        List[Student]: Liste de tous les élèves
    """
    return db.query(Student).all()


def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
    """
    Récupère un élève par son identifiant.

    Args:
        db: Session SQLAlchemy active
        student_id: Identifiant de l'élève recherché

    Returns:
        Optional[Student]: L'élève trouvé ou None si inexistant
    """
    return db.query(Student).filter(Student.id == student_id).first()


def get_students_count(db: Session) -> int:
    """
    Compte le nombre total d'élèves dans la base.

    Args:
        db: Session SQLAlchemy active

    Returns:
        int: Nombre total d'élèves
    """
    return db.query(func.count(Student.id)).scalar() or 0


def create_student(db: Session, nom: str, note_math: float,
                   heures_etude: float, orientation: str) -> Student:
    """
    Crée un nouvel élève dans la base de données.

    Args:
        db: Session SQLAlchemy active
        nom: Nom de l'élève
        note_math: Note de mathématiques
        heures_etude: Heures d'étude par semaine
        orientation: Orientation recommandée

    Returns:
        Student: L'élève créé avec son identifiant
    """
    student = Student(
        nom=nom,
        note_math=note_math,
        heures_etude=heures_etude,
        orientation=orientation
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_students_bulk(db: Session, students_data: List[dict]) -> int:
    """
    Crée plusieurs élèves en une seule opération (bulk insert).

    Args:
        db: Session SQLAlchemy active
        students_data: Liste de dictionnaires contenant les données des élèves

    Returns:
        int: Nombre d'élèves créés
    """
    students = [
        Student(
            nom=data["nom"],
            note_math=data["note_math"],
            heures_etude=data["heures_etude"],
            orientation=data["orientation"]
        )
        for data in students_data
    ]
    db.add_all(students)
    db.commit()
    return len(students)


def delete_all_students(db: Session) -> int:
    """
    Supprime tous les élèves de la base de données.

    Attention : Cette opération est destructive et irréversible.

    Args:
        db: Session SQLAlchemy active

    Returns:
        int: Nombre d'élèves supprimés
    """
    count = get_students_count(db)
    db.query(Student).delete()
    db.commit()
    return count


def delete_student_by_id(db: Session, student_id: int) -> bool:
    """
    Supprime un élève par son identifiant.

    Args:
        db: Session SQLAlchemy active
        student_id: Identifiant de l'élève à supprimer

    Returns:
        bool: True si l'élève a été supprimé, False s'il n'existait pas
    """
    student = get_student_by_id(db, student_id)
    if student:
        db.delete(student)
        db.commit()
        return True
    return False
