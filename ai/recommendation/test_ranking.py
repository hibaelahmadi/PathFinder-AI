
from ranking import rank_programs

student = {
    "interests": ["informatique", "ia", "mathématiques"],
    "grades": {"mathématiques": 17, "physique": 15},
    "skills": ["programmation", "logique"],
    "career_goal": "ingénieur ia",
    "preferred_type": "public"
}

programs = [
    {
        "name": "Informatique",
        "interests": ["informatique", "mathématiques"],
        "required_subjects": ["mathématiques", "physique"],
        "skills": ["programmation", "logique"],
        "career_paths": ["ingénieur ia"],
        "type": "public"
    },
    {
        "name": "Gestion",
        "interests": ["gestion", "économie"],
        "required_subjects": ["mathématiques"],
        "skills": ["communication", "organisation"],
        "career_paths": ["manager"],
        "type": "public"
    },
    {
        "name": "Mathématiques appliquées",
        "interests": ["mathématiques", "ia"],
        "required_subjects": ["mathématiques"],
        "skills": ["logique"],
        "career_paths": ["data scientist"],
        "type": "public"
    }
]

results = rank_programs(student, programs, top_n=3)

for index, result in enumerate(results, start=1):
    print(
        f"{index}. {result['program']} "
        f"- {result['score']}/100"
    )

assert len(results) == 3
assert results[0]["program"] == "Informatique"
assert results[0]["score"] == 95.0
