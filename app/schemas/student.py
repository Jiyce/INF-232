"""
Schémas Pydantic pour la validation des données des élèves.

Ce module définit les classes de validation utilisées par FastAPI
pour garantir l'intégrité des données entrantes et sortantes de l'API.
"""

from pydantic import BaseModel, Field, ConfigDict


class StudentBase(BaseModel):
    """
    Schéma de base pour un élève avec les champs communs.

    Ce schéma est utilisé comme classe parente pour la création
    et la réponse des données d'élève.

    Attributes:
        nom: Nom complet de l'élève (1-100 caractères)
        note_math: Note de mathématiques sur 20 (0-20)
        heures_etude: Heures d'étude par semaine (0-100)
        orientation: Orientation recommandée
    """

    nom: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nom complet de l'élève",
        examples=["Jean Dupont"]
    )

    note_math: float = Field(
        ...,
        ge=1,
        le=20,
        description="Note de mathématiques sur 20",
        examples=[14.5]
    )

    heures_etude: float = Field(
        ...,
        ge=0,
        le=100,
        description="Nombre d'heures d'étude par semaine",
        examples=[15.5]
    )

    orientation: str = Field(
        ...,
        pattern="^(Scientifique|Littéraire)$",
        description="Orientation recommandée",
        examples=["Scientifique"]
    )


class StudentCreate(StudentBase):
    """
    Schéma pour la création d'un nouvel élève.

    Hérite de StudentBase sans ajouter de champs supplémentaires.
    L'identifiant est généré automatiquement par la base de données.
    """
    pass


class StudentResponse(StudentBase):
    """
    Schéma pour la réponse API contenant un élève complet.

    Étend StudentBase en ajoutant l'identifiant unique généré par la base.

    Attributes:
        id: Identifiant unique de l'élève dans la base de données
    """

    id: int = Field(
        ...,
        description="Identifiant unique de l'élève",
        examples=[1]
    )

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    """
    Schéma pour la réponse API contenant une liste d'élèves.

    Attributes:
        total: Nombre total d'élèves
        students: Liste des élèves
    """

    total: int = Field(
        ...,
        description="Nombre total d'élèves"
    )

    students: list[StudentResponse] = Field(
        ...,
        description="Liste des élèves"
    )


class GenerationParams(BaseModel):
    """
    Schéma pour les paramètres de génération des données.

    Attributes:
        chef_groupe: Nom du chef de groupe utilisé comme graine
        count: Nombre d'élèves à générer (défaut: 250)
    """

    chef_groupe: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nom complet du chef de groupe (utilisé comme graine)",
        examples=["Marie Curie"]
    )

    count: int = Field(
        default=250,
        ge=1,
        le=1000,
        description="Nombre d'élèves à générer"
    )
