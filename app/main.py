"""
Point d'entrée principal de l'application FastAPI.

Ce module initialise l'application FastAPI, configure les middlewares,
mount les fichiers statiques et inclut l'ensemble des routeurs.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR
from app.database import create_tables
from app.models.student import Student  # noqa: F401 - Import pour création des tables
from app.utils.logging_config import setup_logging

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application.

    Crée les tables au démarrage et effectue le nettoyage à l'arrêt.
    """
    logger.info("Démarrage de l'application Lycée Analytics...")
    create_tables()
    logger.info("Tables de base de données initialisées.")
    yield
    logger.info("Arrêt de l'application Lycée Analytics.")


# Création de l'application FastAPI
app = FastAPI(
    title="Lycée Analytics",
    description="Application d'analyse des performances des élèves de Terminale",
    version="1.1.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Montage des fichiers statiques (CSS, JS, images)
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

# Configuration des templates Jinja2
from jinja2 import Environment, FileSystemLoader
jinja_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))

# Wrapper compatible avec l'ancienne API starlette (name, context)
# et la nouvelle API (request, name, context)
class CompatibleTemplates:
    """Wrapper compatible multi-versions pour Jinja2Templates."""

    def __init__(self, env):
        self.env = env

    def TemplateResponse(self, name, context):
        """Rend un template avec l'API legacy (name, context)."""
        from starlette.templating import _TemplateResponse
        template = self.env.get_template(name)
        return _TemplateResponse(template, context)

templates = CompatibleTemplates(jinja_env)


# Import et inclusion des routeurs
from app.routers import pages, api_students, api_stats, api_export  # noqa: E402

app.include_router(pages.router)
app.include_router(api_students.router, prefix="/api/students", tags=["students"])
app.include_router(api_stats.router, prefix="/api/stats", tags=["statistics"])
app.include_router(api_export.router, prefix="/api/export", tags=["export"])

logger.info("Routeurs inclus : pages, api_students, api_stats, api_export")


@app.get("/health")
async def health_check():
    """
    Endpoint de vérification de santé de l'application.

    Returns:
        dict: Statut de l'application
    """
    return {"status": "ok", "message": "Lycée Analytics is running"}
