"""
Module de configuration de l'application.

Ce module centralise tous les paramètres de configuration de l'application,
notamment les chemins de fichiers et les paramètres de la base de données.
"""

import os
from pathlib import Path

# Répertoire racine du projet
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Répertoire des données
DATA_DIR: Path = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Chemin de la base de données SQLite
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATA_DIR / 'lycee.db'}"
)

# Paramètres de génération des données
DEFAULT_STUDENT_COUNT: int = 250
SEED_PREFIX: str = "lycee_analytics"

# Paramètres des graphiques
PLOTLY_TEMPLATE: str = "plotly_white"
CHART_HEIGHT: int = 500

# Paramètres du modèle de classification
TEST_SIZE: float = 0.2
RANDOM_STATE: int = 42
