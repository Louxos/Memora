"""Journalisation locale de Memora.

Fichier rotatif dans <données>/logs/memora.log. Les clés API ne sont
jamais écrites dans les logs (voir masquer()).
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from memora.config import paths

_LOG_FORMAT = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s"
_configuré = False


def masquer(secret: str | None) -> str:
    """Rend une valeur secrète inoffensive pour affichage / logs."""
    if not secret:
        return ""
    if len(secret) <= 8:
        return "••••"
    return f"{secret[:4]}…{secret[-4:]}"


def configurer_logger(niveau=logging.INFO) -> logging.Logger:
    """Initialise le logger racine Memora (idempotent)."""
    global _configuré
    logger = logging.getLogger("memora")
    if _configuré:
        return logger
    logger.setLevel(niveau)
    try:
        handler = RotatingFileHandler(
            paths.logs_dir() / "memora.log",
            maxBytes=512_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
    except OSError:  # répertoire en lecture seule : logs console seulement
        pass
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(_LOG_FORMAT))
    logger.addHandler(console)
    logger.propagate = False
    _configuré = True
    return logger


def logger(name: str) -> logging.Logger:
    return logging.getLogger(f"memora.{name}")
