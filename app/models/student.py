"""
Modèle SQLAlchemy pour la table des élèves.

Ce module définit la structure de la table `students` dans la base de données,
représentant les élèves de Terminale avec leurs performances scolaires.
"""

from enum import Enum as PyEnum

from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Orientation(str, PyEnum):
    """
    Énumération des orientations possibles pour un élève de Terminale.

    Cette énumération garantit que seules les valeurs valides sont utilisées
    dans la base de données, évitant les erreurs de saisie.
    """
    SCIENTIFIQUE = "Scientifique"
    LITTERAIRE = "Littéraire"


class Student(Base):
    """
    Modèle de données pour un élève de Terminale.

    Cette classe représente la table `students` dans la base de données SQLite.
    Chaque instance correspond à un élève avec ses caractéristiques scolaires.

    Attributes:
        id: Identifiant unique auto-incrémenté (clé primaire)
        nom: Nom complet de l'élève
        note_math: Note de mathématiques sur 20 (0-20)
        heures_etude: Nombre d'heures d'étude par semaine
        orientation: Orientation recommandée (Scientifique ou Littéraire)
    """

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Identifiant unique de l'élève"
    )

    nom: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Nom complet de l'élève"
    )

    note_math: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Note de mathématiques sur 20"
    )

    heures_etude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Nombre d'heures d'étude par semaine"
    )

    orientation: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Orientation recommandée (Scientifique ou Littéraire)"
    )

    def __repr__(self) -> str:
        """
        Représentation textuelle de l'objet Student.

        Returns:
            str: Description concise de l'élève
        """
        return (
            f"<Student(id={self.id}, nom='{self.nom}', "
            f"note_math={self.note_math:.2f}, "
            f"heures_etude={self.heures_etude:.1f}, "
            f"orientation='{self.orientation}')>"
        )

    def to_dict(self) -> dict:
        """
        Convertit l'objet en dictionnaire pour la sérialisation JSON.

        Returns:
            dict: Représentation dictionnaire de l'élève
        """
        return {
            "id": self.id,
            "nom": self.nom,
            "note_math": self.note_math,
            "heures_etude": self.heures_etude,
            "orientation": self.orientation,
        }
