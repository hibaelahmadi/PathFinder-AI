"""Lecture seule de la configuration Gemini, sans journaliser les secrets."""

import os
from pathlib import Path


def charger_cle_gemini():
    """Privilégie l'environnement non vide, puis le .env racine."""
    cle = os.environ.get("GEMINI_API_KEY")
    if isinstance(cle, str) and cle.strip():
        return cle.strip()
    from dotenv import dotenv_values

    cle = dotenv_values(
        Path(__file__).resolve().parents[2] / ".env",
        interpolate=False, encoding="utf-8-sig",
    ).get("GEMINI_API_KEY")
    if isinstance(cle, str) and cle.strip():
        return cle.strip()
    raise ValueError("Configuration Gemini absente ou vide")
