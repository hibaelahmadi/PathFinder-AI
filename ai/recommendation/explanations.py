"""Explications fondées sur les informations disponibles."""


def generate_explanations(student, program):
    explanations = []

    # Intérêts communs.
    interests = student.get("interests")
    program_interests = program.get("interests")

    if interests is not None and program_interests:
        common = set(interests) & set(program_interests)

        if common:
            explanations.append(
                f"Tes intérêts en {', '.join(sorted(common))} "
                "correspondent à cette formation."
            )

    # Points forts scolaires, uniquement avec des notes connues.
    grades = student.get("grades") or {}
    subjects = program.get("required_subjects") or []

    strengths = [
        subject
        for subject in subjects
        if grades.get(subject) is not None
        and grades[subject] >= 14
    ]

    if strengths:
        explanations.append(
            f"Tes bons résultats en {', '.join(strengths)} "
            "constituent un point fort."
        )

    # Compétences communes.
    skills = student.get("skills")
    program_skills = program.get("skills")

    if skills is not None and program_skills:
        common = set(skills) & set(program_skills)

        if common:
            explanations.append(
                f"Tes compétences en {', '.join(sorted(common))} "
                "sont pertinentes pour cette formation."
            )

    # Objectif professionnel.
    goal = student.get("career_goal")
    career_paths = program.get("career_paths") or []

    if goal and goal in career_paths:
        explanations.append(
            f"Cette formation est cohérente avec ton objectif : {goal}."
        )

    # Préférence d'établissement.
    preferred_type = student.get("preferred_type")

    if (
        preferred_type is not None
        and preferred_type == program.get("type")
    ):
        explanations.append(
            "Le type d'établissement correspond à ta préférence."
        )

    if not explanations:
        explanations.append(
            "Les informations disponibles ne permettent pas "
            "de justifier une correspondance positive avec ton profil."
        )

    return explanations