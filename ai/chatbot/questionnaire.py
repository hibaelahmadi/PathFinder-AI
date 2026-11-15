def choisir_question_interets(interets):
    """Choisit une question de précision selon les intérêts."""
    texte = (interets or "").strip().lower()

    if "informatique" in texte:
        return (
            "Qu'est-ce qui t'attire en informatique : "
            "programmation, réseaux, données ou autre ? "
        )

    if "biologie" in texte:
        return (
            "Qu'est-ce qui t'attire en biologie : "
            "santé, recherche, environnement ou autre ? "
        )

    return (
        "Peux-tu donner un exemple d'activité que tu aimes ? "
        "Tu peux passer avec Entrée. "
    )


QUESTIONS = {
    "bac": "Quelle est ta série de bac ? ",
    "ville_souhaitee": "Dans quelle ville souhaites-tu étudier ? ",
    "interets": "Quelles matières ou activités aimes-tu ? ",
    "mobilite": (
        "Acceptes-tu d'étudier dans une autre ville ? "
        "(oui / non / je ne sais pas) "
    ),
    "autres_villes": (
        "Quelles autres villes envisages-tu ? "
        "Tu peux écrire « aucune préférence ». "
    ),
    "objectif": (
        "Quel métier ou domaine aimerais-tu explorer ? "
        "Tu peux répondre « je ne sais pas ». "
    ),
    "competences_declarees": (
        "Dans quelles activités te sens-tu à l'aise ? "
        "Par exemple : analyser, créer, communiquer, aider, "
        "résoudre des problèmes. Tu peux passer avec Entrée. "
    ),
}


def creer_profil():
    """Prépare un profil vide pour un nouvel entretien."""
    return {
        "bac": None,
        "ville_souhaitee": None,
        "interets": None,
        "precision_interets": None,
        "mobilite": None,
        "autres_villes": None,
        "objectif": None,
        "competences_declarees": None,
        "confirme": False,
    }
def prochaine_question(reponses):
    """Renvoie la prochaine question, ou None si le résumé est prêt."""
    ordre = [
        "bac",
        "ville_souhaitee",
        "interets",
        "precision_interets",
        "mobilite",
        "autres_villes",
        "objectif",
        "competences_declarees",
    ]

    for code in ordre:
        # On demande les autres villes seulement si la mobilité est acceptée.
        if code == "autres_villes":
            if reponses.get("mobilite") != "oui":
                continue

        # Un champ présent a déjà été traité, même si sa réponse est vide.
        if code in reponses:
            continue

        if code == "precision_interets":
            texte = choisir_question_interets(reponses.get("interets"))
        else:
            texte = QUESTIONS[code]

        return {
            "question_code": code,
            "question_text": texte,
        }

    return None


def traiter_reponse(reponses, question_code, answer_text):
    """Valide la réponse attendue et renvoie un nouvel état du questionnaire."""
    actualisees = reponses.copy()
    question = prochaine_question(reponses)
    errors = []

    if question is None:
        errors.append("Toutes les questions ont déjà été traitées.")
    elif question_code != question["question_code"]:
        errors.append("Le code ne correspond pas à la question attendue.")

    if not isinstance(answer_text, str):
        errors.append("La réponse doit être une chaîne de caractères.")
    elif not errors:
        valeur = answer_text.strip()
        if question_code == "mobilite":
            valeur = valeur.lower()
            if valeur not in ("oui", "non", "je ne sais pas"):
                errors.append("Écris oui, non ou je ne sais pas.")
        else:
            valeur = valeur or None

        if not errors:
            actualisees[question_code] = valeur

    suivante = prochaine_question(actualisees)
    return {
        "reponses": actualisees,
        "next_question": suivante,
        "ready_for_confirmation": suivante is None,
        "errors": errors,
    }
