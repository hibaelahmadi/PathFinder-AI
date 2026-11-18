"""Calcul de compatibilité à partir des données disponibles."""

WEIGHTS = {
    "interests": 0.30,
    "academic": 0.25,
    "skills": 0.20,
    "goals": 0.15,
    "preferences": 0.10,
}


def calculate_score(student, program):
    scores = {}

    # Intérêts : None signifie inconnu ; [] signifie aucun déclaré.
    interests = student.get("interests")
    program_interests = program.get("interests")

    if interests is not None and program_interests:
        expected = set(program_interests)
        scores["interests"] = len(set(interests) & expected) / len(expected)

    # Notes : seules les notes renseignées sont utilisées.
    grades = student.get("grades")
    subjects = program.get("required_subjects")

    if grades is not None and subjects:
        known_grades = [
            grades[subject]
            for subject in subjects
            if grades.get(subject) is not None
        ]

        if known_grades:
            for grade in known_grades:
                if (
                    isinstance(grade, bool)
                    or not isinstance(grade, (int, float))
                    or not 0 <= grade <= 20
                ):
                    raise ValueError("Chaque note doit être entre 0 et 20.")

            scores["academic"] = (
                sum(known_grades) / len(known_grades) / 20
            )

    # Compétences.
    skills = student.get("skills")
    program_skills = program.get("skills")

    if skills is not None and program_skills:
        expected = set(program_skills)
        scores["skills"] = len(set(skills) & expected) / len(expected)

    # Objectif : nécessite des valeurs harmonisées avec le catalogue.
    goal = student.get("career_goal")
    career_paths = program.get("career_paths")

    if goal and career_paths:
        scores["goals"] = float(goal in career_paths)

    # Public / privé : aucune préférence n'entraîne aucune pénalité.
    preferred_type = student.get("preferred_type")
    program_type = program.get("type")

    if preferred_type is not None and program_type is not None:
        scores["preferences"] = float(preferred_type == program_type)

    if not scores:
        return None

    available_weight = sum(WEIGHTS[key] for key in scores)

    weighted_score = sum(
        WEIGHTS[key] * value
        for key, value in scores.items()
    )

    return round(100 * weighted_score / available_weight, 2)