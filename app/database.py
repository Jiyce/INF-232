"""
Module de gestion de la base de données.

Ce module configure la connexion SQLAlchemy à la base SQLite et fournit
les utilitaires pour créer les tables et gérer les sessions.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DATABASE_URL

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite avec FastAPI
)

# Session locale pour les opérations DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base déclarative pour les modèles
Base = declarative_base()


def get_db():
    """
    Générateur de session de base de données pour FastAPI.

    Yields:
        Session: Session SQLAlchemy active

    Example:
        Utilisé comme dépendance FastAPI::

            @app.get("/items/")
            def read_items(db: Session = Depends(get_db)):
                ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """
    Crée toutes les tables définies dans les modèles.

    Cette fonction doit être appelée au démarrage de l'application
    pour s'assurer que la structure de la base de données existe.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """
    Supprime toutes les tables existantes.

    Attention : Cette fonction est destructive et supprime toutes les données.
    À utiliser avec précaution, principalement pour les tests ou la régénération.
    """
    Base.metadata.drop_all(bind=engine)
