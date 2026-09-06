"""Gestion des erreurs de Memora.

Chaque erreur métier expose un message clair, en français, directement
affichable à l'utilisateur — jamais de traceback brut.
"""

from __future__ import annotations


class MemoraError(Exception):
    """Erreur de l'application avec un message compréhensible."""

    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details


class ApiKeyMissingError(MemoraError):
    pass


class ApiKeyInvalidError(MemoraError):
    pass


class ApiQuotaError(MemoraError):
    pass


class ApiUnavailableError(MemoraError):
    pass


class NetworkError(MemoraError):
    pass


class AiResponseError(MemoraError):
    pass


class DocumentTooLargeError(MemoraError):
    pass


class DocumentUnreadableError(MemoraError):
    pass


class UnsupportedFormatError(MemoraError):
    pass
