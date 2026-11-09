
# PathFinder AI - Recommendation Engine
# Module: scoring.py

WEIGHTS = {
    "interests": 0.30,
    "academic": 0.25,
    "skills": 0.20,
    "goals": 0.15,
    "preferences": 0.10
}


def calculate_score(student, program):
    """
    Calculate compatibility between a student
    and an academic program.

    Returns a score between 0 and 100.
    """

    # 1. Calculate interest compatibility
    student_interests = set(student["interests"])
    program_interests = set(program["interests"])

    interest_score = (
        len(student_interests & program_interests)
        / len(program_interests)
        if program_interests else 0
    )

    # 2. Calculate academic compatibility
    required_subjects = program["required_subjects"]

    if required_subjects:
        academic_score = sum(
            min(student["grades"].get(subject, 0) / 20, 1)
            for subject in required_subjects
        ) / len(required_subjects)
    else:
        academic_score = 0

    # 3. Calculate skills compatibility
    student_skills = set(student["skills"])
    program_skills = set(program["skills"])

    skill_score = (
        len(student_skills & program_skills)
        / len(program_skills)
        if program_skills else 0
    )

    # 4. Calculate career goal compatibility
    goal_score = (
        1.0
        if student["career_goal"] in program["career_paths"]
        else 0.0
    )

    # 5. Calculate preference compatibility
    preference_score = (
        1.0
        if student["preferred_type"] == program["type"]
        else 0.0
    )

    # 6. Calculate final weighted score
    final_score = 100 * (
        WEIGHTS["interests"] * interest_score
        + WEIGHTS["academic"] * academic_score
        + WEIGHTS["skills"] * skill_score
        + WEIGHTS["goals"] * goal_score
        + WEIGHTS["preferences"] * preference_score
    )

    return round(final_score, 2)

