"""
Configuration centralisée du logging pour l'application.

Ce module configure le logging avec des handlers pour la console et les fichiers,
en respectant les bonnes pratiques de la PEP8 et de la qualité logicielle.
"""

import logging
import logging.handlers
import os
from pathlib import Path

from app.config import BASE_DIR


def setup_logging(
    level: int = logging.INFO,
    log_dir: str = None,
    app_name: str = "lycee_analytics"
) -> logging.Logger:
    """
    Configure le logging pour l'application.

    Args:
        level: Niveau de logging (défaut: INFO)
        log_dir: Répertoire des logs (défaut: BASE_DIR/logs)
        app_name: Nom de l'application

    Returns:
        logging.Logger: Logger configuré
    """
    if log_dir is None:
        log_dir = BASE_DIR / "logs"
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)

    # Formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    simple_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )

    # Logger principal
    logger = logging.getLogger(app_name)
    logger.setLevel(level)

    # Éviter les handlers dupliqués
    if logger.handlers:
        return logger

    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # Handler fichier rotatif
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / f"{app_name}.log",
        maxBytes=5_242_880,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Handler fichier erreurs
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / f"{app_name}_errors.log",
        maxBytes=2_097_152,  # 2 MB
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)

    logger.info("Logging configuré avec succès")
    return logger


def get_logger(name: str = "lycee_analytics") -> logging.Logger:
    """
    Récupère un logger configuré.

    Args:
        name: Nom du logger

    Returns:
        logging.Logger: Logger configuré
    """
    return logging.getLogger(name)
