
from scoring import calculate_score

student = {
    "interests": [
        "informatique",
        "ia",
        "mathématiques"
    ],
    "grades": {
        "mathématiques": 17,
        "physique": 15
    },
    "skills": [
        "programmation",
        "logique"
    ],
    "career_goal": "ingénieur ia",
    "preferred_type": "public"
}

program = {
    "name": "Formation fictive en informatique",
    "interests": [
        "informatique",
        "mathématiques"
    ],
    "required_subjects": [
        "mathématiques",
        "physique"
    ],
    "skills": [
        "programmation",
        "logique"
    ],
    "career_paths": [
        "ingénieur ia",
        "développeur"
    ],
    "type": "public"
}

score = calculate_score(student, program)

print("Formation :", program["name"])
print("Score de compatibilité :", score, "/100")

assert score == 95.0
