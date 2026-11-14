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