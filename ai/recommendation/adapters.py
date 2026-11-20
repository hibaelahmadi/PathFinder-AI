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

        # Textes libres conservés sans modification.
        "interests_text": profile.get(
            "interets_texte_original",
            profile.get("interets"),
        ),
        "interest_details_text": profile.get(
            "precision_interets_texte_original",
            profile.get("precision_interets"),
        ),
        "skills_text": profile.get(
            "competences_texte_original",
            profile.get("competences_declarees"),
        ),
        "career_goal_text": profile.get(
            "objectif_texte_original",
            profile.get("objectif"),
        ),

        # Codes structurés utilisés par le scoring.
        "interests": profile.get("categories_interets"),
        "skills": profile.get("categories_competences"),
        "career_goal": profile.get("code_metier"),

        # Données encore indisponibles : aucune valeur inventée.
        "grades": profile.get("notes"),
        "max_annual_budget": profile.get("budget_annuel_max"),
        "preferred_type": profile.get("type_etablissement"),

        "profile_confirmed": profile.get("confirme") is True,
    }

def adapt_p4_program(program, institution):
    """Adapte une formation P4 avec son établissement."""
    if program["institution_id"] != institution["institution_id"]:
        raise ValueError("La formation et l'établissement ne correspondent pas.")

    adapted = program.copy()

    # Identifiant P4 conservé comme chaîne.
    adapted["id"] = program["program_id"]
    adapted["code"] = program["program_id"]

    sector = institution.get("sector")
    adapted["type"] = sector if sector in ("public", "prive") else None

    adapted["institution_name"] = institution.get("name")
    adapted["city_status"] = institution.get("city_status")

    # Une ville de rattachement ou un réseau ne suffit pas
    # à exclure une formation pour mobilité impossible.
    entity_type = institution.get("entity_type") or ""
    uncertain_city = (
        institution.get("city_status") != "registre"
        or entity_type.startswith("reseau")
    )

    adapted["city"] = (
        None if uncertain_city else institution.get("city")
    )

    return adapted