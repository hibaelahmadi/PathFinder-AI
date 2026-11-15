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