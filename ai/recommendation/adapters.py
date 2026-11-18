"""Adaptation du profil du chatbot vers le moteur de recommandation."""


def adapt_student_profile(profile):
    """Convertit les champs connus sans inventer les données absentes."""
    if not isinstance(profile, dict):
        raise TypeError("Le profil doit être un dictionnaire.")

    mobility = profile.get("mobilite")

    if isinstance(mobility, str):
        mobility = mobility.strip().lower()

    mobility_mapping = {
        "oui": True,
        "non": False,
        "je ne sais pas": None,
    }

    return {
        "bac_type": profile.get("bac"),
        "preferred_city": profile.get("ville_souhaitee"),
        "can_relocate": mobility_mapping.get(mobility),
        "other_cities_text": profile.get("autres_villes"),

        # Textes conservés en attendant les catégories de Nada/Hafssa.
        "interests_text": profile.get("interets"),
        "interest_details_text": profile.get("precision_interets"),
        "skills_text": profile.get("competences_declarees"),
        "career_goal": profile.get("objectif"),

        # Données encore indisponibles : aucune valeur inventée.
        "interests": None,
        "skills": None,
        "grades": profile.get("notes"),
        "max_annual_budget": profile.get("budget_annuel_max"),
        "preferred_type": profile.get("type_etablissement"),

        "profile_confirmed": profile.get("confirme") is True,
    }