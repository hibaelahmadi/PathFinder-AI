
# PathFinder AI - Recommendation Explanations


def generate_explanations(student, program):
    """
    Generate explanations for a recommended program.
    """

    explanations = []

    # 1. Common interests
    common_interests = set(student["interests"]) & set(
        program["interests"]
    )

    if common_interests:
        interests = ", ".join(sorted(common_interests))
        explanations.append(
            f"Tes intérêts en {interests} correspondent "
            "à cette formation."
        )

    # 2. Academic strengths
    relevant_subjects = [
        subject
        for subject in program["required_subjects"]
        if subject in student["grades"]
        and student["grades"][subject] >= 14
    ]

    if relevant_subjects:
        subjects = ", ".join(relevant_subjects)
        explanations.append(
            f"Tes bons résultats en {subjects} "
            "constituent un point fort."
        )

    # 3. Common skills
    common_skills = set(student["skills"]) & set(
        program["skills"]
    )

    if common_skills:
        skills = ", ".join(sorted(common_skills))
        explanations.append(
            f"Tes compétences en {skills} "
            "sont pertinentes pour cette formation."
        )

    # 4. Career goal
    if student["career_goal"] in program["career_paths"]:
        explanations.append(
            "Cette formation est cohérente avec "
            f"ton objectif : {student['career_goal']}."
        )

    # 5. Institution preference
    if student["preferred_type"] == program["type"]:
        explanations.append(
            "Le type d'établissement correspond "
            "à ta préférence."
        )

    if not explanations:
        explanations.append(
            "Cette formation nécessite une exploration "
            "complémentaire de ton profil."
        )

    return explanations
