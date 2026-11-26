"""Reconnaissance locale des variantes A/B pour les parcours du chatbot."""

import re
import unicodedata


def reconnaitre_sciences_mathematiques(texte):
    """Renvoie l'original, un code interne A/B ou None et une clarification.

    Le code interne A/B est traduit en code draft-1 par le questionnaire.
    Une déclaration contradictoire, incertaine ou négative ne fixe aucun code.
    """
    resultat = {
        "original_text": texte,
        "code": None,
        "clarification_needed": False,
        "clarification_question": None,
        "errors": [],
    }
    if not isinstance(texte, str):
        resultat["errors"] = ["La réponse doit être une chaîne de caractères."]
        return resultat

    normalise = "".join(
        lettre for lettre in unicodedata.normalize("NFD", texte.casefold())
        if unicodedata.category(lettre) != "Mn"
    )
    mention = re.search(r"\bsciences\s+mathematiques\b", normalise)
    if not mention:
        return resultat

    resultat["clarification_needed"] = True
    resultat["clarification_question"] = (
        "Ta série est-elle Sciences mathématiques A ou B ? "
        "Tu peux répondre « je ne sais pas »."
    )
    # Reconnaissance volontairement stricte : seul un libellé explicite,
    # éventuellement précédé d'une déclaration simple, est accepté.
    declaration = re.fullmatch(
        r"\s*(?:(?:je suis en|j['’]ai un bac|mon bac est|ma serie est)\s+)?"
        r"(?:bac\s+)?sciences\s+mathematiques\s+([ab])\s*[.!]?\s*",
        normalise,
    )
    if declaration:
        resultat["code"] = declaration.group(1).upper()
        resultat["clarification_needed"] = False
        resultat["clarification_question"] = None
    return resultat
