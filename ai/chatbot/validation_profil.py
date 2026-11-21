"""Validation isolée des futures notes et frais de scolarité annuels."""

import math


def _valider_nombre(texte, maximum=None):
    if not isinstance(texte, str):
        return {"value": None, "errors": ["La réponse doit être une chaîne de caractères."]}

    texte = texte.strip()
    if not texte:
        return {"value": None, "errors": []}

    try:
        valeur = float(texte.replace(",", "."))
    except ValueError:
        return {"value": None, "errors": ["La réponse doit être un nombre."]}

    if not math.isfinite(valeur):
        return {"value": None, "errors": ["Le nombre doit être fini."]}
    if valeur < 0 or (maximum is not None and valeur > maximum):
        message = (
            "La note doit être comprise entre 0 et 20 inclus."
            if maximum is not None
            else "Le budget doit être supérieur ou égal à 0 DH par an."
        )
        return {"value": None, "errors": [message]}
    return {"value": valeur, "errors": []}


def valider_note(texte):
    """Valide une note sur 20 ; une chaîne vide reste non renseignée."""
    return _valider_nombre(texte, maximum=20)


def valider_budget_annuel(texte):
    """Valide les frais de scolarité seuls, en DH/an, sans plafond imposé."""
    return _valider_nombre(texte)


def valider_type_etablissement(texte):
    """Normalise le type souhaité ; vide et sans préférence donnent None."""
    if not isinstance(texte, str):
        return {"value": None, "errors": ["La réponse doit être une chaîne de caractères."]}

    texte = texte.strip().lower()
    valeurs = {
        "public": "public",
        "privé": "prive",
        "prive": "prive",
        "sans préférence": None,
        "sans preference": None,
        "": None,
    }
    if texte not in valeurs:
        return {"value": None, "errors": ["Écris public, privé ou sans préférence."]}
    return {"value": valeurs[texte], "errors": []}
